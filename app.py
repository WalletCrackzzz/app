import sys
import random
import json
import requests
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QLineEdit, QProgressBar, 
                             QFrame, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

def download_icon():
    icon_url = "https://raw.githubusercontent.com/WalletCrackzzz/app/main/icon.ico"
    icon_path = "wallet_checker.ico"
    
    if not os.path.exists(icon_path):
        try:
            response = requests.get(icon_url)
            if response.status_code == 200:
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
        except:
            pass
    return icon_path if os.path.exists(icon_path) else None

class LicenseWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("License Activation")
        self.setFixedSize(500, 600)
        self.valid_licenses = self.load_licenses()
        
        # Set window icon
        icon_path = download_icon()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
            
        self.setup_ui()
        
    def load_licenses(self):
        try:
            # Load from GitHub
            url = "https://raw.githubusercontent.com/WalletCrackzzz/app/main/credentials.json"
            response = requests.get(url)
            if response.status_code == 200:
                return json.loads(response.text)
            
            # Fallback to local file
            with open("licenses.txt", "r") as f:
                return [line.strip() for line in f if line.strip()]
        except:
            # Default licenses if both methods fail
            return [
                "PRO-LICENSE-2024",
                "ULTRA-WALLET-SCAN",
                "CRYPTO-CHECKER-VIP",
                "WALLET-HUNTER-X",
                "SEED-PHARSE-MASTER"
            ]
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("License Activation")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Version comparison
        versions_layout = QVBoxLayout()
        
        # DEMO version
        demo_frame = QFrame()
        demo_frame.setFrameShape(QFrame.StyledPanel)
        demo_layout = QVBoxLayout()
        demo_layout.setContentsMargins(10, 10, 10, 10)
        
        demo_title = QLabel("DEMO Version")
        demo_title.setFont(QFont("Arial", 12, QFont.Bold))
        demo_title.setAlignment(Qt.AlignCenter)
        demo_layout.addWidget(demo_title)
        
        demo_features = QLabel(
            "• 100K checks max\n"
            "• 2 blockchains max\n"
            "• Basic scanning\n"
            "• Finds 1 wallet at 100K\n"
            "• No saving functionality"
        )
        demo_features.setFont(QFont("Arial", 10))
        demo_layout.addWidget(demo_features)
        
        demo_frame.setLayout(demo_layout)
        versions_layout.addWidget(demo_frame)
        
        # Licensed version
        licensed_frame = QFrame()
        licensed_frame.setFrameShape(QFrame.StyledPanel)
        licensed_layout = QVBoxLayout()
        licensed_layout.setContentsMargins(10, 10, 10, 10)
        
        licensed_title = QLabel("Licensed Version")
        licensed_title.setFont(QFont("Arial", 12, QFont.Bold))
        licensed_title.setAlignment(Qt.AlignCenter)
        licensed_layout.addWidget(licensed_title)
        
        licensed_features = QLabel(
            "• Unlimited checks\n"
            "• 6+ blockchains\n"
            "• Advanced algorithms\n"
            "• Priority support\n"
            "• 10x faster\n"
            "• Save results"
        )
        licensed_features.setFont(QFont("Arial", 10))
        licensed_layout.addWidget(licensed_features)
        
        licensed_frame.setLayout(licensed_layout)
        versions_layout.addWidget(licensed_frame)
        
        layout.addLayout(versions_layout)
        
        # License input
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Paste your license key here...")
        self.license_input.setFont(QFont("Arial", 10))
        layout.addWidget(self.license_input)
        
        activate_btn = QPushButton("ACTIVATE LICENSE")
        activate_btn.setFont(QFont("Arial", 10, QFont.Bold))
        activate_btn.setStyleSheet("background-color: #660066; color: white;")
        activate_btn.clicked.connect(self.activate_license)
        layout.addWidget(activate_btn)
        
        # Sample keys
        sample_label = QLabel("Example License Keys:")
        sample_label.setFont(QFont("Arial", 9, QFont.Bold))
        layout.addWidget(sample_label)
        
        sample_keys = QLabel("\n".join(self.valid_licenses[:3]))  # Show first 3 as examples
        sample_keys.setFont(QFont("Courier New", 9))
        layout.addWidget(sample_keys)
        
        # Telegram button
        telegram_btn = QPushButton("GET LICENSED VERSION ON TELEGRAM")
        telegram_btn.setFont(QFont("Arial", 10, QFont.Bold))
        telegram_btn.setStyleSheet("background-color: #0088cc; color: white;")
        telegram_btn.clicked.connect(self.open_telegram)
        layout.addWidget(telegram_btn)
        
        central_widget.setLayout(layout)
    
    def activate_license(self):
        license_key = self.license_input.text().strip()
        
        if license_key in self.valid_licenses:
            # Save activated license
            with open("activated_license.txt", "w") as f:
                f.write(license_key)
            
            QMessageBox.information(self, "Success", "Software successfully activated!")
            self.parent.activate_license(license_key)
            self.close()
        else:
            self.license_input.setStyleSheet("border: 2px solid red;")
            QTimer.singleShot(1000, lambda: self.license_input.setStyleSheet(""))
            QMessageBox.warning(self, "Invalid License", "Wrong license key entered. Please try again.")
    
    def open_telegram(self):
        import webbrowser
        webbrowser.open("https://t.me/Walletcrackzzz")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.licensed = False
        self.scanning = False
        self.found_count = 0
        self.setWindowTitle("Wallet Finder by @Walletcrackz")
        self.setFixedSize(800, 600)
        
        # Set window icon
        icon_path = download_icon()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        self.central_widget.setLayout(self.main_layout)
        
        # BIP39 words list (partial - add full list later)
        self.bip39_words = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
            # ... (add all words here)
            "zone", "zoo"
        ]
        
        # Create UI
        self.create_ui()
        
        # Scanning timer
        self.checked_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_checking)
    
    def create_ui(self):
        # Header
        header = QLabel("Wallet Finder by @Walletcrackz")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(header)
        
        # Status bar
        self.status_bar = QLabel("Status: DEMO Version (Stopped)")
        self.status_bar.setFont(QFont("Arial", 10))
        self.status_bar.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.status_bar)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("START SCAN")
        self.start_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.start_btn.setStyleSheet("background-color: #006600; color: white;")
        self.start_btn.clicked.connect(self.toggle_scan)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("STOP SCAN")
        self.stop_btn.setFont(QFont("Arial", 10))
        self.stop_btn.setStyleSheet("background-color: #660000; color: white;")
        self.stop_btn.clicked.connect(self.toggle_scan)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.main_layout.addLayout(control_layout)
        
        # Progress area
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100000)
        progress_layout.addWidget(self.progress_bar)
        
        self.checked_label = QLabel("# Checked: 0")
        self.checked_label.setFont(QFont("Arial", 10))
        progress_layout.addWidget(self.checked_label)
        
        self.main_layout.addLayout(progress_layout)
        
        # Results area
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setFont(QFont("Courier New", 9))
        self.main_layout.addWidget(self.results_area)
        
        # Found section
        found_frame = QFrame()
        found_layout = QVBoxLayout()
        
        found_title = QLabel("SCAN RESULTS")
        found_title.setFont(QFont("Arial", 12, QFont.Bold))
        found_title.setAlignment(Qt.AlignCenter)
        found_layout.addWidget(found_title)
        
        self.found_label = QLabel("Found: 0")
        self.found_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.found_label.setAlignment(Qt.AlignCenter)
        found_layout.addWidget(self.found_label)
        
        found_frame.setLayout(found_layout)
        self.main_layout.addWidget(found_frame)
        
        # Button area
        button_layout = QHBoxLayout()
        
        telegram_btn = QPushButton("GET LICENSED VERSION")
        telegram_btn.setFont(QFont("Arial", 10))
        telegram_btn.setStyleSheet("background-color: #0088cc; color: white;")
        telegram_btn.clicked.connect(self.open_telegram)
        button_layout.addWidget(telegram_btn)
        
        license_btn = QPushButton("ACTIVATE LICENSE")
        license_btn.setFont(QFont("Arial", 10, QFont.Bold))
        license_btn.setStyleSheet("background-color: #660066; color: white;")
        license_btn.clicked.connect(self.show_license_window)
        button_layout.addWidget(license_btn)
        
        self.main_layout.addLayout(button_layout)
    
    def show_license_window(self):
        self.license_window = LicenseWindow(self)
        self.license_window.show()
    
    def open_telegram(self):
        import webbrowser
        webbrowser.open("https://t.me/Walletcrackzzz")
    
    def toggle_scan(self):
        self.scanning = not self.scanning
        
        if self.scanning:
            if not self.licensed and self.checked_count >= 100000:
                QMessageBox.information(self, "DEMO Limit Reached", 
                    "You've reached the DEMO limit of 100K checks.\nActivate license to continue.")
                self.scanning = False
                return
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_bar.setText(f"Status: {'Licensed' if self.licensed else 'DEMO'} Version (Scanning)")
            self.timer.start(100)
        else:
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_bar.setText(f"Status: {'Licensed' if self.licensed else 'DEMO'} Version (Stopped)")
            self.timer.stop()
    
    def simulate_checking(self):
        increment = random.randint(50, 200)
        self.checked_count += increment
        self.checked_label.setText(f"# Checked: {self.checked_count}")
        self.progress_bar.setValue(self.checked_count % 100000)
        
        # DEMO version finds exactly 1 wallet at 100K checks
        if not self.licensed and self.checked_count >= 100000 and self.checked_count - increment < 100000:
            self.found_count = 1
            self.found_label.setText("Found: 1")
            self.results_area.append("\n=== DEMO WALLET FOUND ===\n")
            self.results_area.append(" ".join(random.sample(self.bip39_words, 12)))
            self.results_area.append("\n=== ACTIVATE LICENSE TO SAVE ===\n")
            self.toggle_scan()
            return
        
        # Regular checking output
        if random.random() < 0.3:
            prefixes = ["Wallet check", "Mac", "What key", "What price?"]
            line = random.choice(prefixes) + " " + " ".join(random.sample(self.bip39_words, random.randint(3, 7)))
            self.results_area.append(line)
            
            # Scroll to bottom
            self.results_area.verticalScrollBar().setValue(
                self.results_area.verticalScrollBar().maximum()
            )
    
    def activate_license(self, license_key):
        self.licensed = True
        self.status_bar.setText("Status: Licensed Version (Stopped)")
        
        # Reset counters
        self.checked_count = 0
        self.checked_label.setText("# Checked: 0")
        self.progress_bar.setValue(0)
        self.found_count = 0
        self.found_label.setText("Found: 0")
        
        if not self.scanning:
            self.results_area.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dark theme
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 0, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 0, 15))
    palette.setColor(QPalette.AlternateBase, QColor(45, 0, 45))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 0, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(150, 0, 150))
    palette.setColor(QPalette.Highlight, QColor(100, 0, 100))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
