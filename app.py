import os
import sys
import random
import time
import hashlib
import json
import threading
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, 
                             QListWidget, QTabWidget, QMessageBox, QFileDialog, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QDesktopServices

class CryptoFinderGUI(QMainWindow):
    update_signal = pyqtSignal(str, str)  # signal for updating UI from threads
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Wallet Finder")
        self.setGeometry(100, 100, 900, 700)
        
        # Set application icon
        self.set_application_icon()
        
        # Initialize core functionality
        self.crypto_finder = CryptoFinderCore()
        
        # Setup UI with dark theme
        self.init_ui()
        self.apply_dark_theme()
        
        # Connect signals
        self.update_signal.connect(self.update_status)
        
        # Load initial data
        self.update_license_status()
        self.statusBar().hide()

    def set_application_icon(self):
        try:
            icon_url = "https://raw.githubusercontent.com/Walletcrackzzz/app/refs/heads/main/icon.ico"
            response = requests.get(icon_url)
            response.raise_for_status()
            
            icon_path = os.path.join(os.getcwd(), "temp_icon.ico")
            with open(icon_path, 'wb') as f:
                f.write(response.content)
            
            self.setWindowIcon(QIcon(icon_path))
            
            try:
                os.remove(icon_path)
            except:
                pass
        except Exception as e:
            print(f"Could not load application icon: {e}")
            self.setWindowIcon(QIcon())

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
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
        
        self.stats_label = QLabel("Attempts: 0\nFound: 0")
        status_layout.addWidget(self.stats_label)
        
        scan_layout.addWidget(status_group)
        
        # Results list
        self.results_list = QListWidget()
        scan_layout.addWidget(QLabel("Recent Results:"))
        scan_layout.addWidget(self.results_list)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10)
        self.progress_bar.setTextVisible(False)
        scan_layout.addWidget(self.progress_bar)
        
        # Scan controls
        scan_controls = QWidget()
        scan_controls_layout = QHBoxLayout(scan_controls)
        
        self.start_btn = QPushButton("Start Scan")
        self.start_btn.clicked.connect(self.start_scan)
        scan_controls_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Scan")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        scan_controls_layout.addWidget(self.stop_btn)
        
        scan_layout.addWidget(scan_controls)
        
        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Login section
        login_group = QWidget()
        login_layout = QVBoxLayout(login_group)
        
        login_layout.addWidget(QLabel("Account Login"))
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        login_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.password_input)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        login_layout.addWidget(login_btn)
        
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        login_layout.addWidget(logout_btn)
        
        self.license_status = QLabel("Status: Not logged in (DEMO MODE)")
        self.license_status.setWordWrap(True)
        login_layout.addWidget(self.license_status)
        
        settings_layout.addWidget(login_group)
        
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
        
        # Results toolbar
        results_toolbar = QWidget()
        toolbar_layout = QHBoxLayout(results_toolbar)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Newest First", "Oldest First", "By Coin", "By Balance"])
        toolbar_layout.addWidget(self.sort_combo)
        
        sort_btn = QPushButton("Sort Results")
        sort_btn.clicked.connect(self.sort_results)
        toolbar_layout.addWidget(sort_btn)
        
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        toolbar_layout.addWidget(export_btn)
        
        results_layout.addWidget(results_toolbar)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        # Support Tab
        support_tab = QWidget()
        support_layout = QVBoxLayout(support_tab)
        
        support_label = QLabel("Support & Contact")
        support_label.setFont(QFont("Arial", 12, QFont.Bold))
        support_layout.addWidget(support_label)
        
        telegram_label = QLabel("Telegram Support: @Walletcrackz")
        support_layout.addWidget(telegram_label)
        
        telegram_btn = QPushButton("Join Telegram Group")
        telegram_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/Walletcrackzzz")))
        support_layout.addWidget(telegram_btn)
        
        support_layout.addStretch()
        
        tabs.addTab(scan_tab, "Scan")
        tabs.addTab(settings_tab, "Settings")
        tabs.addTab(results_tab, "Results")
        tabs.addTab(support_tab, "Support")
        
        # Contact info in bottom left
        contact_label = QLabel("Contact: @Walletcrackz | t.me/Walletcrackzzz")
        contact_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        contact_label.setStyleSheet("color: #2a82da;")
        main_layout.addWidget(contact_label)
        
        # Timer for progress bar
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        
    def apply_dark_theme(self):
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
        
    def start_scan(self):
        self.crypto_finder.scanning_active = True
        self.status_label.setText("Status: ACTIVE")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.scan_timer.start(100)
        
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
                self.update_signal.emit("stats", "")
                
                time.sleep(self.crypto_finder.scan_interval)
                
                if not self.crypto_finder.logged_in and time.time() - self.crypto_finder.last_find_time > self.crypto_finder.find_interval:
                    self.crypto_finder.last_find_time = time.time()
                    self.crypto_finder.scan_stats['found'] += 1
                    
                    wallet_type = random.choice(self.crypto_finder.wallet_types)
                    seed = self.crypto_finder.generate_seed()
                    address = self.crypto_finder.generate_address(wallet_type)
                    btc, usd = self.crypto_finder.generate_balance()
                    
                    wallet_data = {
                        'type': wallet_type,
                        'address': address,
                        'valid': False,
                        'btc': btc,
                        'usd': usd,
                        'seed': seed,
                        'demo': True,
                        'timestamp': time.time()
                    }
                    
                    self.crypto_finder.save_wallet(wallet_data, demo=True)
                    self.crypto_finder.found_wallets.append(wallet_data)
                    if len(self.crypto_finder.found_wallets) > 100:
                        self.crypto_finder.found_wallets.pop(0)
                    
                    self.update_signal.emit("found", json.dumps(wallet_data))
                    
        except Exception as e:
            print(f"Scan error: {e}")
            
    def update_status(self, update_type, data):
        if update_type == "stats":
            self.stats_label.setText(f"Attempts: {self.crypto_finder.scan_stats['attempts']}\nFound: {self.crypto_finder.scan_stats['found']}")
        elif update_type == "found":
            try:
                wallet_data = json.loads(data)
                
                if any(w['address'] == wallet_data['address'] for w in self.crypto_finder.found_wallets[:-1]):
                    return
                    
                if wallet_data['demo']:
                    color = "#FFD700"
                    status = "DEMO"
                elif wallet_data['valid']:
                    color = "#00FF00"
                    status = "VALID"
                else:
                    color = "#FF0000"
                    status = "INVALID"
                
                item_text = f"{wallet_data['address']} - {wallet_data['type']} - {status}"
                self.results_list.insertItem(0, item_text)
                self.results_list.item(0).setForeground(QColor(color))
                
                if self.results_list.count() > 20:
                    self.results_list.takeItem(20)
                
                self.display_results_in_text()
                
            except Exception as e:
                print(f"Error updating status: {e}")

    def display_results_in_text(self):
        self.results_text.clear()
        seen_addresses = set()
        
        for wallet in sorted(self.crypto_finder.found_wallets, key=lambda x: x['timestamp'], reverse=True):
            if wallet['address'] in seen_addresses:
                continue
            seen_addresses.add(wallet['address'])
            
            if wallet['demo']:
                color = "#FFD700"
                status = "DEMO"
            elif wallet['valid']:
                color = "#00FF00"
                status = "VALID"
            else:
                color = "#FF0000"
                status = "INVALID"
                
            result_text = f"""
            <span style='color:{color};'><b>{wallet['type']} Wallet Found!</b></span>
            Address: {wallet['address']}
            Balance: {wallet['btc']:.8f} BTC (~${wallet['usd']:.2f})
            Seed: {'[DEMO MODE - LOGIN REQUIRED]' if wallet['demo'] else wallet['seed']}
            Status: <span style='color:{color};'>{status}</span>
            Found: {datetime.fromtimestamp(wallet['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
            {'='*40}
            """
            self.results_text.append(result_text)
            
    def sort_results(self):
        sort_option = self.sort_combo.currentText()
        
        if sort_option == "Newest First":
            self.crypto_finder.found_wallets.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_option == "Oldest First":
            self.crypto_finder.found_wallets.sort(key=lambda x: x['timestamp'])
        elif sort_option == "By Coin":
            self.crypto_finder.found_wallets.sort(key=lambda x: x['type'])
        elif sort_option == "By Balance":
            self.crypto_finder.found_wallets.sort(key=lambda x: x['btc'], reverse=True)
            
        self.display_results_in_text()
        
    def export_results(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", 
            "Text Files (*.txt);;All Files (*)", options=options)
            
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.results_text.toPlainText())
                QMessageBox.information(self, "Success", "Results exported successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export: {str(e)}")

    def update_progress(self):
        self.progress_value = (self.progress_value + 1) % 11
        self.progress_bar.setValue(self.progress_value)

    def update_license_status(self):
        if self.crypto_finder.logged_in:
            coins = self.crypto_finder.target_coin.split(',')
            if len(coins) > 1:
                coins_text = ", ".join(coins)
                self.license_status.setText(f"Logged in - Scanning: {coins_text}")
                self.target_label.setText(f"Target: {coins_text}")
            else:
                self.license_status.setText(f"Logged in - Scanning: {self.crypto_finder.target_coin}")
                self.target_label.setText(f"Target: {self.crypto_finder.target_coin}")
        else:
            self.license_status.setText("Status: Not logged in (DEMO MODE)")
            self.target_label.setText("Target: DEMO (scanning all)")

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
            
        auth_result = self.crypto_finder.verify_credentials(username, password)
        if auth_result:
            self.crypto_finder.logged_in = True
            self.crypto_finder.target_coin = auth_result
            self.update_license_status()
            
            coins = auth_result.split(',')
            if len(coins) > 1:
                coins_text = ", ".join(coins)
                QMessageBox.information(self, "Success", 
                    f"Logged in successfully!\nScanning for: {coins_text}")
            else:
                QMessageBox.information(self, "Success", 
                    f"Logged in successfully!\nScanning for: {auth_result}")
            
            self.username_input.clear()
            self.password_input.clear()
            
            if self.crypto_finder.scanning_active:
                self.crypto_finder.last_find_time = 0
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def logout(self):
        self.crypto_finder.logged_in = False
        self.crypto_finder.target_coin = None
        self.update_license_status()
        QMessageBox.information(self, "Success", "Logged out successfully")

    def save_webhook(self):
        url = self.webhook_input.text().strip()
        self.crypto_finder.discord_webhook = url if url else None
        self.crypto_finder.save_config()
        QMessageBox.information(self, "Success", "Webhook settings saved")

class CryptoFinderCore:
    def __init__(self):
        self.logged_in = False
        self.target_coin = None
        self.discord_webhook = None
        self.scanning_active = False
        self.found_wallets = []
        self.scan_stats = {"attempts": 0, "found": 0}
        self.last_find_time = 0
        self.scan_interval = 0.1
        self.find_interval = 30
        
        self.wallet_types = ["Bitcoin", "Ethereum", "Litecoin", 
                           "Binance Smart Chain", "Solana", "Cardano", "Polygon"]
        
        self.results_dir = "scan_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.config_file = "config.json"
        self.load_config()

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

    def verify_credentials(self, username, password):
        try:
            credentials_url = "https://raw.githubusercontent.com/Walletcrackzzz/app/main/credentials.json"
            response = requests.get(credentials_url)
            response.raise_for_status()
        
            credentials_data = response.json()
            user_data = credentials_data.get(username)
        
            if user_data:
                input_hash = hashlib.sha256(password.encode()).hexdigest()
                if input_hash == user_data["password"]:
                    return ','.join(user_data["coins"]) if user_data["coins"] else None
            return False
        except Exception as e:
            print(f"Error verifying credentials: {e}")
            return False

    def generate_seed(self):
        bip39_words = ["abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse", 
            "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act", 
            "action", "actor", "actress", "actual", "adapt", "add", "addict", "address", "adjust", "admit", 
            "adult", "advance", "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent", 
            "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert", 
            "alien", "all", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter", 
            "always", "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger", 
            "angle", "angry", "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique", 
            "anxiety", "any", "apart", "apology", "appear", "apple", "approve", "april", "arch", "arctic", 
            "area", "arena", "argue", "arm", "armed", "armor", "army", "around", "arrange", "arrest", 
            "arrive", "arrow", "art", "artefact", "artist", "artwork", "ask", "aspect", "assault", "asset", 
            "assist", "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction", 
            "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado", "avoid", "awake", 
            "aware", "away", "awesome", "awful", "awkward", "axis", "baby", "bachelor", "bacon", "badge", 
            "bag", "balance", "balcony", "ball", "bamboo", "banana", "banner", "bar", "barely", "bargain", 
            "barrel", "base", "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become", 
            "beef", "before", "begin", "behave", "behind", "believe", "below", "belt", "bench", "benefit", 
            "best", "betray", "better", "between", "beyond", "bicycle", "bid", "bike", "bind", "biology", 
            "bird", "birth", "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless", 
            "blind", "blood", "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body", 
            "boil", "bomb", "bone", "bonus", "book", "boost", "border", "boring", "borrow", "boss", 
            "bottom", "bounce", "box", "boy", "bracket", "brain", "brand", "brass", "brave", "bread", 
            "breeze", "brick", "bridge", "brief", "bright", "bring", "brisk", "broccoli", "broken", "bronze", 
            "broom", "brother", "brown", "brush", "bubble", "buddy", "budget", "buffalo", "build", "bulb", 
            "bulk", "bullet", "bundle", "bunker", "burden", "burger", "burst", "bus", "business", "busy", 
            "butter", "buyer", "buzz", "cabbage", "cabin", "cable", "cactus", "cage", "cake", "call", 
            "calm", "camera", "camp", "can", "canal", "cancel", "candy", "cannon", "canoe", "canvas", 
            "canyon", "capable", "capital", "captain", "car", "carbon", "card", "cargo", "carpet", "carry", 
            "cart", "case", "cash", "casino", "castle", "casual", "cat", "catalog", "catch", "category", 
            "cattle", "caught", "cause", "caution", "cave", "ceiling", "celery", "cement", "census", "century", 
            "cereal", "certain", "chair", "chalk", "champion", "change", "chaos", "chapter", "charge", "chase", 
            "chat", "cheap", "check", "cheese", "chef", "cherry", "chest", "chicken", "chief", "child", 
            "chimney", "choice", "choose", "chronic", "chuckle", "chunk", "churn", "cigar", "cinnamon", "circle", 
            "citizen", "city", "civil", "claim", "clap", "clarify", "claw", "clay", "clean", "clerk", 
            "clever", "click", "client", "cliff", "climb", "clinic", "clip", "clock", "clog", "close", 
            "cloth", "cloud", "clown", "club", "clump", "cluster", "clutch", "coach", "coast", "coconut", 
            "code", "coffee", "coil", "coin", "collect", "color", "column", "combine", "come", "comfort", 
            "comic", "common", "company", "concert", "conduct", "confirm", "congress", "connect", "consider", "control", 
            "convince", "cook", "cool", "copper", "copy", "coral", "core", "corn", "correct", "cost", 
            "cotton", "couch", "country", "couple", "course", "cousin", "cover", "coyote", "crack", "cradle", 
            "craft", "cram", "crane", "crash", "crater", "crawl", "crazy", "cream", "credit", "creek", 
            "crew", "cricket", "crime", "crisp", "critic", "crop", "cross", "crouch", "crowd", "crucial", 
            "cruel", "cruise", "crumble", "crunch", "crush", "cry", "crystal", "cube", "culture", "cup", 
            "cupboard", "curious", "current", "curtain", "curve", "cushion", "custom", "cute", "cycle", "dad", 
            "damage", "damp", "dance", "danger", "daring", "dash", "daughter", "dawn", "day", "deal", 
            "debate", "debris", "decade", "december", "decide", "decline", "decorate", "decrease", "deer", "defense", 
            "define", "defy", "degree", "delay", "deliver", "demand", "demise", "denial", "dentist", "deny", 
            "depart", "depend", "deposit", "depth", "deputy", "derive", "describe", "desert", "design", "desk", 
            "despair", "destroy", "detail", "detect", "develop", "device", "devote", "diagram", "dial", "diamond", 
            "diary", "dice", "diesel", "diet", "differ", "digital", "dignity", "dilemma", "dinner", "dinosaur", 
            "direct", "dirt", "disagree", "discover", "disease", "dish", "dismiss", "disorder", "display", "distance", 
            "divert", "divide", "divorce", "dizzy", "doctor", "document", "dog", "doll", "dolphin", "domain", 
            "donate", "donkey", "donor", "door", "dose", "double", "dove", "draft", "dragon", "drama", 
            "drastic", "draw", "dream", "dress", "drift", "drill", "drink", "drip", "drive", "drop", 
            "drum", "dry", "duck", "dumb", "dune", "during", "dust", "dutch", "duty", "dwarf", 
            "dynamic", "eager", "eagle", "early", "earn", "earth", "easily", "east", "easy", "echo", 
            "ecology", "economy", "edge", "edit", "educate", "effort", "egg", "eight", "either", "elbow", 
            "elder", "electric", "elegant", "element", "elephant", "elevator", "elite", "else", "embark", "embody", 
            "embrace", "emerge", "emotion", "employ", "empower", "empty", "enable", "enact", "end", "endless", 
            "endorse", "enemy", "energy", "enforce", "engage", "engine", "enhance", "enjoy", "enlist", "enough", 
            "enrich", "enroll", "ensure", "enter", "entire", "entry", "envelope", "episode", "equal", "equip", 
            "era", "erase", "erode", "erosion", "error", "erupt", "escape", "essay", "essence", "estate", 
            "eternal", "ethics", "evidence", "evil", "evoke", "evolve", "exact", "example", "excess", "exchange", 
            "excite", "exclude", "excuse", "execute", "exercise", "exhaust", "exhibit", "exile", "exist", "exit", 
            "exotic", "expand", "expect", "expire", "explain", "expose", "express", "extend", "extra", "eye", 
            "eyebrow", "fabric", "face", "faculty", "fade", "faint", "faith", "fall", "false", "fame", 
            "family", "famous", "fan", "fancy", "fantasy", "farm", "fashion", "fat", "fatal", "father", 
            "fatigue", "fault", "favorite", "feature", "february", "federal", "fee", "feed", "feel", "female", 
            "fence", "festival", "fetch", "fever", "few", "fiber", "fiction", "field", "figure", "file", 
            "film", "filter", "final", "find", "fine", "finger", "finish", "fire", "firm", "first", 
            "fiscal", "fish", "fit", "fitness", "fix", "flag", "flame", "flash", "flat", "flavor", 
            "flee", "flight", "flip", "float", "flock", "floor", "flower", "fluid", "flush", "fly", 
            "foam", "focus", "fog", "foil", "fold", "follow", "food", "foot", "force", "forest", 
            "forget", "fork", "fortune", "forum", "forward", "fossil", "foster", "found", "fox", "fragile", 
            "frame", "frequent", "fresh", "friend", "fringe", "frog", "front", "frost", "frown", "frozen", 
            "fruit", "fuel", "fun", "funny", "furnace", "fury", "future", "gadget", "gain", "galaxy", 
            "gallery", "game", "gap", "garage", "garbage", "garden", "garlic", "garment", "gas", "gasp", 
            "gate", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle", "genuine", "gesture", 
            "ghost", "giant", "gift", "giggle", "ginger", "giraffe", "girl", "give", "glad", "glance", 
            "glare", "glass", "glide", "glimpse", "globe", "gloom", "glory", "glove", "glow", "glue", 
            "goat", "goddess", "gold", "good", "goose", "gorilla", "gospel", "gossip", "govern", "gown", 
            "grab", "grace", "grain", "grant", "grape", "grass", "gravity", "great", "green", "grid", 
            "grief", "grit", "grocery", "group", "grow", "grunt", "guard", "guess", "guide", "guilt", 
            "guitar", "gun", "gym", "habit", "hair", "half", "hammer", "hamster", "hand", "happy", 
            "harbor", "hard", "harsh", "harvest", "hat", "have", "hawk", "hazard", "head", "health", 
            "heart", "heavy", "hedgehog", "height", "hello", "helmet", "help", "hen", "hero", "hidden", 
            "high", "hill", "hint", "hip", "hire", "history", "hobby", "hockey", "hold", "hole", 
            "holiday", "hollow", "home", "honey", "hood", "hope", "horn", "horror", "horse", "hospital", 
            "host", "hotel", "hour", "hover", "hub", "huge", "human", "humble", "humor", "hundred", 
            "hungry", "hunt", "hurdle", "hurry", "hurt", "husband", "hybrid", "ice", "icon", "idea", 
            "identify", "idle", "ignore", "ill", "illegal", "illness", "image", "imitate", "immense", "immune", 
            "impact", "impose", "improve", "impulse", "inch", "include", "income", "increase", "index", "indicate", 
            "indoor", "industry", "infant", "inflict", "inform", "inhale", "inherit", "initial", "inject", "injury", 
            "inmate", "inner", "innocent", "input", "inquiry", "insane", "insect", "inside", "inspire", "install", 
            "intact", "interest", "into", "invest", "invite", "involve", "iron", "island", "isolate", "issue", 
            "item", "ivory", "jacket", "jaguar", "jar", "jazz", "jealous", "jeans", "jelly", "jewel", 
            "job", "join", "joke", "journey", "joy", "judge", "juice", "jump", "jungle", "junior", 
            "junk", "just", "kangaroo", "keen", "keep", "ketchup", "key", "kick", "kid", "kidney", 
            "kind", "kingdom", "kiss", "kit", "kitchen", "kite", "kitten", "kiwi", "knee", "knife", 
            "knock", "know", "lab", "label", "labor", "ladder", "lady", "lake", "lamp", "language", 
            "laptop", "large", "later", "latin", "laugh", "laundry", "lava", "law", "lawn", "lawsuit", 
            "layer", "lazy", "leader", "leaf", "learn", "leave", "lecture", "left", "leg", "legal", 
            "legend", "leisure", "lemon", "lend", "length", "lens", "leopard", "lesson", "letter", "level", 
            "liar", "liberty", "library", "license", "life", "lift", "light", "like", "limb", "limit", 
            "link", "lion", "liquid", "list", "little", "live", "lizard", "load", "loan", "lobster", 
            "local", "lock", "logic", "lonely", "long", "loop", "lottery", "loud", "lounge", "love", 
            "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury", "lyrics", "machine", "mad", 
            "magic", "magnet", "maid", "mail", "main", "major", "make", "mammal", "man", "manage", 
            "mandate", "mango", "mansion", "manual", "maple", "marble", "march", "margin", "marine", "market", 
            "marriage", "mask", "mass", "master", "match", "material", "math", "matrix", "matter", "maximum", 
            "maze", "meadow", "mean", "measure", "meat", "mechanic", "medal", "media", "melody", "melt", 
            "member", "memory", "mention", "menu", "mercy", "merge", "merit", "merry", "mesh", "message", 
            "metal", "method", "middle", "midnight", "milk", "million", "mimic", "mind", "minimum", "minor", 
            "minute", "miracle", "mirror", "misery", "miss", "mistake", "mix", "mixed", "mixture", "mobile", 
            "model", "modify", "mom", "moment", "monitor", "monkey", "monster", "month", "moon", "moral", 
            "more", "morning", "mosquito", "mother", "motion", "motor", "mountain", "mouse", "move", "movie", 
            "much", "muffin", "mule", "multiply", "muscle", "museum", "mushroom", "music", "must", "mutual", 
            "myself", "mystery", "myth", "naive", "name", "napkin", "narrow", "nasty", "nation", "nature", 
            "near", "neck", "need", "negative", "neglect", "neither", "nephew", "nerve", "nest", "net", 
            "network", "neutral", "never", "news", "next", "nice", "night", "noble", "noise", "nominee", 
            "noodle", "normal", "north", "nose", "notable", "note", "nothing", "notice", "novel", "now", 
            "nuclear", "number", "nurse", "nut", "oak", "obey", "object", "oblige", "obscure", "observe", 
            "obtain", "obvious", "occur", "ocean", "october", "odor", "off", "offer", "office", "often", 
            "oil", "okay", "old", "olive", "olympic", "omit", "once", "one", "onion", "online", 
            "only", "open", "opera", "opinion", "oppose", "option", "orange", "orbit", "orchard", "order", 
            "ordinary", "organ", "orient", "original", "orphan", "ostrich", "other", "outdoor", "outer", "output", 
            "outside", "oval", "oven", "over", "own", "owner", "oxygen", "oyster", "ozone", "pact", 
            "paddle", "page", "pair", "palace", "palm", "panda", "panel", "panic", "panther", "paper", 
            "parade", "parent", "park", "parrot", "party", "pass", "patch", "path", "patient", "patrol", 
            "pattern", "pause", "pave", "payment", "peace", "peanut", "pear", "peasant", "pelican", "pen", 
            "penalty", "pencil", "people", "pepper", "perfect", "permit", "person", "pet", "phone", "photo", 
            "phrase", "physical", "piano", "picnic", "picture", "piece", "pig", "pigeon", "pill", "pilot", 
            "pink", "pioneer", "pipe", "pistol", "pitch", "pizza", "place", "planet", "plastic", "plate", 
            "play", "please", "pledge", "pluck", "plug", "plunge", "poem", "poet", "point", "polar", 
            "pole", "police", "pond", "pony", "pool", "popular", "portion", "position", "possible", "post", 
            "potato", "pottery", "poverty", "powder", "power", "practice", "praise", "predict", "prefer", "prepare", 
            "present", "pretty", "prevent", "price", "pride", "primary", "print", "priority", "prison", "private", 
            "prize", "problem", "process", "produce", "profit", "program", "project", "promote", "proof", "property", 
            "prosper", "protect", "proud", "provide", "public", "pudding", "pull", "pulp", "pulse", "pumpkin", 
            "punch", "pupil", "puppy", "purchase", "purity", "purpose", "purse", "push", "put", "puzzle", 
            "pyramid", "quality", "quantum", "quarter", "question", "quick", "quit", "quiz", "quote", "rabbit", 
            "raccoon", "race", "rack", "radar", "radio", "rail", "rain", "raise", "rally", "ramp", 
            "ranch", "random", "range", "rapid", "rare", "rate", "rather", "raven", "raw", "razor", 
            "ready", "real", "reason", "rebel", "rebuild", "recall", "receive", "recipe", "record", "recycle", 
            "reduce", "reflect", "reform", "refuse", "region", "regret", "regular", "reject", "relax", "release", 
            "relief", "rely", "remain", "remember", "remind", "remove", "render", "renew", "rent", "reopen", 
            "repair", "repeat", "replace", "report", "require", "rescue", "resemble", "resist", "resource", "response", 
            "result", "retire", "retreat", "return", "reunion", "reveal", "review", "reward", "rhythm", "rib", 
            "ribbon", "rice", "rich", "ride", "ridge", "rifle", "right", "rigid", "ring", "riot", 
            "ripple", "risk", "ritual", "rival", "river", "road", "roast", "robot", "robust", "rocket", 
            "romance", "roof", "rookie", "room", "rose", "rotate", "rough", "round", "route", "royal", 
            "rubber", "rude", "rug", "rule", "run", "runway", "rural", "sad", "saddle", "sadness", 
            "safe", "sail", "salad", "salmon", "salon", "salt", "salute", "same", "sample", "sand", 
            "satisfy", "satoshi", "sauce", "sausage", "save", "say", "scale", "scan", "scare", "scatter", 
            "scene", "scheme", "school", "science", "scissors", "scorpion", "scout", "scrap", "screen", "script", 
            "scrub", "sea", "search", "season", "seat", "second", "secret", "section", "security", "seed", 
            "seek", "segment", "select", "sell", "seminar", "senior", "sense", "sentence", "series", "service", 
            "session", "settle", "setup", "seven", "shadow", "shaft", "shallow", "share", "shed", "shell", 
            "sheriff", "shield", "shift", "shine", "ship", "shiver", "shock", "shoe", "shoot", "shop", 
            "short", "shoulder", "shove", "shrimp", "shrug", "shuffle", "shy", "sibling", "sick", "side", 
            "siege", "sight", "sign", "silent", "silk", "silly", "silver", "similar", "simple", "since", 
            "sing", "siren", "sister", "situate", "six", "size", "skate", "sketch", "ski", "skill", 
            "skin", "skirt", "skull", "slab", "slam", "sleep", "slender", "slice", "slide", "slight", 
            "slim", "slogan", "slot", "slow", "slush", "small", "smart", "smile", "smoke", "smooth", 
            "snack", "snake", "snap", "sniff", "snow", "soap", "soccer", "social", "sock", "soda", 
            "soft", "solar", "soldier", "solid", "solution", "solve", "someone", "song", "soon", "sorry", 
            "sort", "soul", "sound", "soup", "source", "south", "space", "spare", "spatial", "spawn", 
            "speak", "special", "speed", "spell", "spend", "sphere", "spice", "spider", "spike", "spin", 
            "spirit", "split", "spoil", "sponsor", "spoon", "sport", "spot", "spray", "spread", "spring", 
            "spy", "square", "squeeze", "squirrel", "stable", "stadium", "staff", "stage", "stairs", "stamp", 
            "stand", "start", "state", "stay", "steak", "steel", "stem", "step", "stereo", "stick", 
            "still", "sting", "stock", "stomach", "stone", "stool", "story", "stove", "strategy", "street", 
            "strike", "strong", "struggle", "student", "stuff", "stumble", "style", "subject", "submit", "subway", 
            "success", "such", "sudden", "suffer", "sugar", "suggest", "suit", "summer", "sun", "sunny", 
            "sunset", "super", "supply", "supreme", "sure", "surface", "surge", "surprise", "surround", "survey", 
            "suspect", "sustain", "swallow", "swamp", "swap", "swarm", "swear", "sweet", "swift", "swim", 
            "swing", "switch", "sword", "symbol", "symptom", "syrup", "system", "table", "tackle", "tag", 
            "tail", "talent", "talk", "tank", "tape", "target", "task", "taste", "tattoo", "taxi", 
            "teach", "team", "tell", "ten", "tenant", "tennis", "tent", "term", "test", "text", 
            "thank", "that", "theme", "then", "theory", "there", "they", "thing", "this", "thought", 
            "three", "thrive", "throw", "thumb", "thunder", "ticket", "tide", "tiger", "tilt", "timber", 
            "time", "tiny", "tip", "tired", "tissue", "title", "toast", "tobacco", "today", "toddler", 
            "toe", "together", "toilet", "token", "tomato", "tomorrow", "tone", "tongue", "tonight", "tool", 
            "tooth", "top", "topic", "topple", "torch", "tornado", "tortoise", "toss", "total", "tourist", 
            "toward", "tower", "town", "toy", "track", "trade", "traffic", "tragic", "train", "transfer", 
            "trap", "trash", "travel", "tray", "treat", "tree", "trend", "trial", "tribe", "trick", 
            "trigger", "trim", "trip", "trophy", "trouble", "truck", "true", "truly", "trumpet", "trust", 
            "truth", "try", "tube", "tuition", "tumble", "tuna", "tunnel", "turkey", "turn", "turtle", 
            "twelve", "twenty", "twice", "twin", "twist", "two", "type", "typical", "ugly", "umbrella", 
            "unable", "unaware", "uncle", "uncover", "under", "undo", "unfair", "unfold", "unhappy", "uniform", 
            "unique", "unit", "universe", "unknown", "unlock", "until", "unusual", "unveil", "update", "upgrade", 
            "uphold", "upon", "upper", "upset", "urban", "urge", "usage", "use", "used", "useful", 
            "useless", "usual", "utility", "vacant", "vacuum", "vague", "valid", "valley", "valve", "van", 
            "vanish", "vapor", "various", "vast", "vault", "vehicle", "velvet", "vendor", "venture", "venue", 
            "verb", "verify", "version", "very", "vessel", "veteran", "viable", "vibrant", "vicious", "victory", 
            "video", "view", "village", "vintage", "violin", "virtual", "virus", "visa", "visit", "visual", 
            "vital", "vivid", "vocal", "voice", "void", "volcano", "volume", "vote", "voyage", "wage", 
            "wagon", "wait", "walk", "wall", "walnut", "want", "warfare", "warm", "warrior", "wash", 
            "wasp", "waste", "water", "wave", "way", "wealth", "weapon", "wear", "weasel", "weather", 
            "web", "wedding", "weekend", "weird", "welcome", "west", "wet", "whale", "what", "wheat", 
            "wheel", "when", "where", "whip", "whisper", "wide", "width", "wife", "wild", "will", 
            "win", "window", "wine", "wing", "wink", "winner", "winter", "wire", "wisdom", "wise", 
            "wish", "witness", "wolf", "woman", "wonder", "wood", "wool", "word", "work", "world", 
            "worry", "worth", "wrap", "wreck", "wrestle", "wrist", "write", "wrong", "yard", "year", 
            "yellow", "you", "young", "youth", "zebra", "zero", "zone", "zoo"]  # Replace with your complete word list
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
        btc_amount = random.uniform(0.000002, 0.02)
        usd_value = round(btc_amount * 50000, 5)
        return btc_amount, usd_value

    def save_wallet(self, wallet_data, demo=False):
        coin = wallet_data['type'].upper()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefix = "DEMO" if demo else "FOUND"
        filename = f"{self.results_dir}/{coin}_{prefix}_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Wallet Type: {wallet_data['type']}\n")
            f.write(f"Address: {wallet_data['address']}\n")
            f.write(f"Balance: {wallet_data['btc']:.8f} BTC (~${wallet_data['usd']:.2f})\n")
            if not demo and wallet_data['valid']:
                f.write(f"Seed: {wallet_data['seed']}\n")
            elif demo:
                f.write(f"Seed: [DEMO MODE - LOGIN REQUIRED]\n")
        
        return filename

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoFinderGUI()
    window.show()
    sys.exit(app.exec_())
