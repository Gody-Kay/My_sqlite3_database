import sys
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from database import verify_user_credentials
from theme import get_app_stylesheet

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotel Management System - Login")
        self.setFixedSize(480, 420)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(get_app_stylesheet())
        
        self.authenticated = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.container = QWidget(self)
        self.container.setObjectName("containerFrame")
        self.container.setStyleSheet("""
            QWidget#containerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:1 #111827);
                border: 1px solid #334155;
                border-radius: 24px;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(28, 28, 28, 28)
        container_layout.setSpacing(14)

        title_label = QLabel("Welcome Back", self)
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #f8fafc;")
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)

        subtitle_label = QLabel("Secure access to your hotel operations", self)
        subtitle_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(subtitle_label)

        container_layout.addSpacing(10)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(42)
        container_layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)
        container_layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Sign In", self)
        self.login_btn.setFixedHeight(44)
        self.login_btn.clicked.connect(self.handle_login)
        container_layout.addWidget(self.login_btn)

        self.close_btn = QPushButton("Cancel", self)
        self.close_btn.setFixedHeight(42)
        self.close_btn.setStyleSheet("""
            QPushButton { background-color: #111827; color: #f8fafc; }
            QPushButton:hover { background-color: #fb7185; color: #ffffff; }
        """)
        self.close_btn.clicked.connect(self.close)
        container_layout.addWidget(self.close_btn)

        footer_label = QLabel("Protected by multi-layer access controls", self)
        footer_label.setStyleSheet("font-size: 11px; color: #60a5fa;")
        footer_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(footer_label)

        layout.addWidget(self.container)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 170))
        self.container.setGraphicsEffect(shadow)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Warning", "Please enter both username and password.")
            return

        if verify_user_credentials(username, password):
            self.authenticated = True
            self.accept()
        else:
            QMessageBox.critical(self, "Access Denied", "Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()