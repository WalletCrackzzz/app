import os
import sys
import random
import time
import hashlib
import json
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, 
                             QListWidget, QTabWidget, QMessageBox, QFileDialog, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

class CryptoFinderGUI(QMainWindow):
    update_signal = pyqtSignal(str, str)  # signal for updating UI from threads
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Wallet Finder")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize core functionality with faster settings
        self.crypto_finder = CryptoFinderCore()
        self.crypto_finder.scan_interval = 0.1  # Much faster scanning (was 1 second)
        self.crypto_finder.find_interval = 30  # Find wallets every 30 seconds (was 60)
        
        # Setup UI with dark theme
        self.init_ui()
        self.apply_dark_theme()
        
        # Connect signals
        self.update_signal.connect(self.update_status)
        
        # Load initial data
        self.update_license_status()
        
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Scan Tab
        scan_tab = QWidget()
        scan_layout = QVBoxLayout(scan_tab)
        
        # Status panel
        status_group = QWidget()
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Status: INACTIVE")
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        status_layout.addWidget(self.status_label)
        
        self.target_label = QLabel("Target: DEMO (scanning all)")
        status_layout.addWidget(self.target_label)
        
        # Stats
        self.stats_label = QLabel("Attempts: 0\nFound: 0")
        status_layout.addWidget(self.stats_label)
        
        scan_layout.addWidget(status_group)
        
        # Results list with color coding
        self.results_list = QListWidget()
        scan_layout.addWidget(QLabel("Recent Results:"))
        scan_layout.addWidget(self.results_list)
        
        # Progress bar with faster animation
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10)
        self.progress_bar.setTextVisible(False)
        scan_layout.addWidget(self.progress_bar)
        
        # Scan controls
        scan_controls = QWidget()
        scan_controls_layout = QHBoxLayout(scan_controls)
        
        self.start_btn = QPushButton("Start Scan")
        self.start_btn.clicked.connect(self.toggle_scan)
        scan_controls_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Scan")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        scan_controls_layout.addWidget(self.stop_btn)
        
        scan_layout.addWidget(scan_controls)
        
        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # License section
        license_group = QWidget()
        license_layout = QVBoxLayout(license_group)
        
        license_layout.addWidget(QLabel("License Activation"))
        
        self.license_status = QLabel("No active licenses (DEMO MODE)")
        self.license_status.setWordWrap(True)
        license_layout.addWidget(self.license_status)
        
        self.license_combo = QComboBox()
        self.license_combo.addItems(["BTC", "ETH", "LTC", "BSC", "SOL", "ADA", "MATIC"])
        license_layout.addWidget(self.license_combo)
        
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Enter license key")
        license_layout.addWidget(self.license_input)
        
        activate_btn = QPushButton("Activate License")
        activate_btn.clicked.connect(self.activate_license)
        license_layout.addWidget(activate_btn)
        
        settings_layout.addWidget(license_group)
        
        # Webhook section
        webhook_group = QWidget()
        webhook_layout = QVBoxLayout(webhook_group)
        
        webhook_layout.addWidget(QLabel("Discord Webhook Setup"))
        
        self.webhook_input = QLineEdit()
        self.webhook_input.setPlaceholderText("Enter webhook URL")
        if self.crypto_finder.discord_webhook:
            self.webhook_input.setText(self.crypto_finder.discord_webhook)
        webhook_layout.addWidget(self.webhook_input)
        
        webhook_btn = QPushButton("Save Webhook")
        webhook_btn.clicked.connect(self.save_webhook)
        webhook_layout.addWidget(webhook_btn)
        
        settings_layout.addWidget(webhook_group)
        settings_layout.addStretch()
        
        # Results Tab
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        results_layout.addWidget(export_btn)
        
        # Add tabs
        tabs.addTab(scan_tab, "Scan")
        tabs.addTab(settings_tab, "Settings")
        tabs.addTab(results_tab, "Results")
        
        # Faster timer for progress bar animation
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        
    def apply_dark_theme(self):
        # Set dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        
        # Additional style tweaks
        self.setStyleSheet("""
            QWidget {
                background-color: #353535;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #444;
            }
            QTabBar::tab {
                background: #353535;
                color: white;
                padding: 8px;
                border: 1px solid #444;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #2a82da;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #252525;
                color: white;
                border: 1px solid #444;
                padding: 5px;
            }
            QPushButton {
                background-color: #353535;
                color: white;
                border: 1px solid #444;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #454545;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
            QComboBox {
                background-color: #252525;
                color: white;
                border: 1px solid #444;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: white;
                selection-background-color: #2a82da;
            }
            QListWidget {
                background-color: #252525;
                color: white;
                border: 1px solid #444;
            }
            QTextEdit {
                background-color: #252525;
                color: white;
                border: 1px solid #444;
            }
            QProgressBar {
                border: 1px solid #444;
                text-align: center;
                background-color: #353535;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                width: 10px;
            }
        """)
        
    def update_progress(self):
        self.progress_value = (self.progress_value + 1) % 11
        self.progress_bar.setValue(self.progress_value)
        
    def toggle_scan(self):
        if not self.crypto_finder.scanning_active:
            self.start_scan()
        else:
            self.stop_scan()
            
    def start_scan(self):
        self.crypto_finder.scanning_active = True
        self.status_label.setText("Status: ACTIVE")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.scan_timer.start(100)  # Faster animation (was 500ms)
        
        # Start scanning in a separate thread
        scan_thread = threading.Thread(target=self.run_scan)
        scan_thread.daemon = True
        scan_thread.start()
        
    def stop_scan(self):
        self.crypto_finder.scanning_active = False
        self.status_label.setText("Status: INACTIVE")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.scan_timer.stop()
        self.progress_bar.setValue(0)
        
    def run_scan(self):
        self.crypto_finder.scan_stats = {"attempts": 0, "found": 0}
        self.crypto_finder.last_find_time = time.time()
        
        try:
            while self.crypto_finder.scanning_active:
                self.crypto_finder.scan_stats['attempts'] += 1
                
                # Update UI
                self.update_signal.emit("stats", "")
                
                # Faster scanning with shorter sleep
                time.sleep(self.crypto_finder.scan_interval)
                
                # Check if we should find a wallet (more frequently now)
                if time.time() - self.crypto_finder.last_find_time > self.crypto_finder.find_interval:
                    self.crypto_finder.last_find_time = time.time()
                    
                    # Determine wallet type
                    if self.crypto_finder.target_coin:
                        wallet_type = self.crypto_finder.target_coin
                        demo = False
                    else:
                        wallet_type = random.choice(self.crypto_finder.wallet_types)
                        demo = True
                    
                    # Generate wallet
                    self.crypto_finder.scan_stats['found'] += 1
                    seed = self.crypto_finder.generate_seed()
                    address = self.crypto_finder.generate_address(wallet_type)
                    btc, usd = self.crypto_finder.generate_balance()
                    valid = not demo and random.random() < 0.7
                    
                    wallet_data = {
                        'type': wallet_type,
                        'address': address,
                        'valid': valid,
                        'btc': btc,
                        'usd': usd,
                        'seed': seed,
                        'demo': demo
                    }
                    
                    # Save wallet
                    filename = self.crypto_finder.save_wallet(wallet_data, demo=demo)
                    
                    # Add to results
                    self.crypto_finder.found_wallets.append(wallet_data)
                    if len(self.crypto_finder.found_wallets) > 10:  # Show more results
                        self.crypto_finder.found_wallets.pop(0)
                    
                    # Update UI with color coding
                    self.update_signal.emit("found", json.dumps(wallet_data))
                    
        except Exception as e:
            print(f"Scan error: {e}")
            
    def update_status(self, update_type, data):
        if update_type == "stats":
            self.stats_label.setText(f"Attempts: {self.crypto_finder.scan_stats['attempts']}\nFound: {self.crypto_finder.scan_stats['found']}")
        elif update_type == "found":
            wallet_data = json.loads(data)
            
            # Determine color based on wallet status
            if wallet_data['demo']:
                color = "#FFD700"  # Gold for demo wallets
                status = "DEMO"
            elif wallet_data['valid']:
                color = "#00FF00"  # Bright green for valid wallets
                status = "VALID"
            else:
                color = "#FF0000"  # Bright red for invalid wallets
                status = "INVALID"
                
            item_text = f"{wallet_data['address']} - {wallet_data['type']} - {status}"
            
            # Add to results list with color
            self.results_list.insertItem(0, item_text)
            self.results_list.item(0).setForeground(QColor(color))
            
            # Keep more results visible (10 instead of 5)
            if self.results_list.count() > 10:
                self.results_list.takeItem(10)
                
            # Add to results text with color formatting
            result_text = f"""
            <span style='color:{color};'><b>{wallet_data['type']} Wallet Found!</b></span>
            Address: {wallet_data['address']}
            Balance: {wallet_data['btc']:.8f} BTC (~${wallet_data['usd']:.2f})
            Seed: {'[DEMO MODE - LICENSE REQUIRED]' if wallet_data['demo'] else wallet_data['seed']}
            Status: <span style='color:{color};'>{status}</span>
            {'='*40}
            """
            self.results_text.append(result_text)
            
    def activate_license(self):
        key = self.license_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Error", "Please enter a license key")
            return
            
        coin = self.license_combo.currentText()
        if coin == "ALL":
            QMessageBox.information(self, "Info", "Demo mode: ALL CHAINS license not available")
            return
            
        if self.crypto_finder.activate_license(key, silent=True):
            self.update_license_status()
            QMessageBox.information(self, "Success", f"{coin} license activated!")
            self.license_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Invalid license key")
            
    def update_license_status(self):
        if self.crypto_finder.active_licenses:
            active = ', '.join(self.crypto_finder.active_licenses)
            self.license_status.setText(f"Active licenses: {active}")
            if self.crypto_finder.target_coin:
                self.target_label.setText(f"Target: {self.crypto_finder.target_coin}")
        else:
            self.license_status.setText("No active licenses (DEMO MODE)")
            self.target_label.setText("Target: DEMO (scanning all)")
            
    def save_webhook(self):
        url = self.webhook_input.text().strip()
        self.crypto_finder.discord_webhook = url if url else None
        self.crypto_finder.save_config()
        QMessageBox.information(self, "Success", "Webhook settings saved")
        
    def export_results(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.results_text.toPlainText())
                QMessageBox.information(self, "Success", "Results exported successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export results: {str(e)}")
                
    def closeEvent(self, event):
        self.crypto_finder.scanning_active = False
        event.accept()

class CryptoFinderCore:
    def __init__(self):
        self.licence_file = "licence.key"
        self.config_file = "config.json"
        self.license_hashes = {
            "BTC": "fe7be411c4424e50cf2515e703a9a8ddd072978319badad323a1fd2563cf6cf7",  # "password"
            "ETH": "8088d115fdc089411abe34de01fecd7963cfb96d4072ea223bfabf99f1050657",  # "ethkey"
            "LTC": "a1be65e54c2e169344a9bf4af76994c28dcfd064ae87cdf88a3fbdfcacb67646",  # "ltckey"
            "BSC": "b970ff00b96116cd02ef28ef3e23bbf6eb82f981f38fc666418fe94c504a73e0",  # "bsckey"
            "SOL": "130f6d230f5f097534c9e14189cb56fbf5b50054ee3bc5ee4ce2cec379b84bc4",  # "solkey"
            "ADA": "5dc490999d69996e82a116502198173e34ec51c58204d8757fa2a535a535a72f",  # "adakey"
            "MATIC": "b38c4cd2145066b2b94bfe0758988b6a46c08ad735948783845df4a170d450c8",  # "matickey"
            "ALL": "6893dd700fec8f3eb2a7a54ba9727f66d043ce3ccf80b34d70f73367b14d02bc"   # "admin"
        }
        self.active_licenses = set()
        self.discord_webhook = None
        self.target_coin = None
        self.scanning_active = False
        self.found_wallets = []
        self.scan_stats = {"attempts": 0, "found": 0}
        self.last_find_time = 0
        self.scan_interval = 0.1  # Faster scanning interval (seconds)
        self.find_interval = 30  # Find wallets every 30 seconds
        
        self.wallet_types = ["Bitcoin", "Ethereum", "Litecoin", 
                           "Binance Smart Chain", "Solana", "Cardano", "Polygon"]
        
        self.results_dir = "scan_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.load_config()
        self.load_licenses()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.discord_webhook = config.get("discord_webhook")
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        config = {"discord_webhook": self.discord_webhook}
        with open(self.config_file, "w") as f:
            json.dump(config, f)

    def load_licenses(self):
        if os.path.exists(self.licence_file):
            try:
                with open(self.licence_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            for coin, valid_hash in self.license_hashes.items():
                                key_hash = hashlib.sha256(line.encode()).hexdigest()
                                if key_hash == valid_hash:
                                    self.active_licenses.add(coin)
                                    if coin != "ALL":
                                        self.target_coin = coin
            except Exception as e:
                print(f"Error loading licenses: {e}")

    def save_licenses(self):
        with open(self.licence_file, "w") as f:
            for coin in self.active_licenses:
                if coin == "BTC":
                    f.write("password\n")
                elif coin == "ETH":
                    f.write("ethkey\n")
                elif coin == "LTC":
                    f.write("ltckey\n")
                elif coin == "BSC":
                    f.write("bsckey\n")
                elif coin == "SOL":
                    f.write("solkey\n")
                elif coin == "ADA":
                    f.write("adakey\n")
                elif coin == "MATIC":
                    f.write("matickey\n")
                elif coin == "ALL":
                    f.write("admin\n")

    def activate_license(self, key, silent=False):
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        if key_hash == self.license_hashes["ALL"]:
            if not silent:
                print(f"Demo mode: ALL CHAINS license not available")
            return False
            
        for coin, valid_hash in self.license_hashes.items():
            if coin == "ALL":
                continue
            if key_hash == valid_hash:
                self.active_licenses.add(coin)
                self.target_coin = coin
                if not silent:
                    print(f"{coin} license activated!")
                    print(f"Now scanning for {coin} wallets only")
                self.save_licenses()
                return True
                
        if not silent:
            print(f"Invalid license key")
        return False

    def is_licensed_for(self, coin):
        return coin.upper() in self.active_licenses

    def generate_seed(self):
        bip39_words = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse", 
            # ... (rest of the BIP39 word list would go here)
            "zone", "zoo"
        ]
        return ' '.join(random.choices(bip39_words, k=12))

    def generate_address(self, wallet_type):
        coin = wallet_type.upper()
        prefixes = {
            "BITCOIN": ["1", "3", "bc1"],
            "ETHEREUM": ["0x"],
            "LITECOIN": ["L", "M", "ltc1"],
            "BINANCE SMART CHAIN": ["0x", "bnb"],
            "SOLANA": ["So"],
            "CARDANO": ["addr"],
            "POLYGON": ["0x"]
        }
        prefix = random.choice(prefixes.get(coin, ["addr"]))
        chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return prefix + ''.join(random.choices(chars, k=33-len(prefix)))

    def generate_balance(self):
        btc_amount = random.uniform(0.000002, 0.0005)
        usd_value = round(btc_amount * 50000, 5)
        return btc_amount, usd_value

    def save_wallet(self, wallet_data, demo=False):
        coin = wallet_data['type'].upper()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefix = "DEMO" if demo else "FOUND"
        filename = f"{self.results_dir}/{coin}_{prefix}_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(f"Wallet Type: {wallet_data['type']}\n")
            f.write(f"Address: {wallet_data['address']}\n")
            f.write(f"Balance: {wallet_data['btc']:.8f} BTC (~${wallet_data['usd']:.2f})\n")
            if not demo and wallet_data['valid']:
                f.write(f"Seed: {wallet_data['seed']}\n")
            elif demo:
                f.write(f"Seed: [DEMO MODE - LICENSE REQUIRED]\n")
        
        return filename

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoFinderGUI()
    window.show()
    sys.exit(app.exec_())
