import sqlite3
import urllib.parse
import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QComboBox, QDialog, QFormLayout, QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from database import get_connection

# Country codes mapping dictionary
COUNTRY_CODES = {
    "Ghana (+233)": "233",
    "Nigeria (+234)": "234",
    "Ivory Coast (+225)": "225",
    "Togo (+228)": "228",
    "United Kingdom (+44)": "44",
    "United States / Canada (+1)": "1"
}

class ComposeMessageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compose Guest Message & WhatsApp")
        self.resize(480, 520)
        self.setStyleSheet("background-color: #1e293b; color: white;")
        
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.recipientCombo = QComboBox()
        
        # Fetch active guests and check if phone column exists in Guests table
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Guests)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "phone" in columns:
            cursor.execute("""
                SELECT g.guest_id, g.full_name, b.room_number, g.phone 
                FROM Bookings b
                JOIN Guests g ON b.guest_id = g.guest_id
                WHERE b.booking_status IN ('Confirmed', 'Checked In')
            """)
            raw_guests = cursor.fetchall()
            self.guests_data = [(g[0], g[1], g[2], g[3] if g[3] else "") for g in raw_guests]
        else:
            cursor.execute("""
                SELECT g.guest_id, g.full_name, b.room_number 
                FROM Bookings b
                JOIN Guests g ON b.guest_id = g.guest_id
                WHERE b.booking_status IN ('Confirmed', 'Checked In')
            """)
            raw_guests = cursor.fetchall()
            self.guests_data = [(g[0], g[1], g[2], "") for g in raw_guests]
            
        conn.close()
        
        if not self.guests_data:
            self.recipientCombo.addItem("No active guests found", None)
            self.recipientCombo.setEnabled(False)
        else:
            self.recipientCombo.addItem("Broadcast to All Guests", ("All", "All", "All", ""))
            for g in self.guests_data:
                self.recipientCombo.addItem(f"{g[1]} (Room {g[2]})", g)
                
        self.recipientCombo.currentIndexChanged.connect(self.on_recipient_changed)
                
        # Message Type Dropdown
        self.typeCombo = QComboBox()
        self.typeCombo.addItems(["WhatsApp Direct Message", "SMS Notification", "Welcome Email", "Custom Announcement"])
        
        # Country Code Selector Dropdown
        self.countryCombo = QComboBox()
        self.countryCombo.addItems(list(COUNTRY_CODES.keys()))
        # Set default to Ghana
        self.countryCombo.setCurrentText("Ghana (+233)")
        
        # Phone Input Field
        self.phoneInput = QLineEdit()
        self.phoneInput.setPlaceholderText("e.g. 0534821057")
        
        self.msgInput = QTextEdit()
        self.msgInput.setPlaceholderText("Type your message here... e.g. Dear guest, your room is ready. Welcome to Apex Horizon Suites!")
        
        input_style = """
            QComboBox, QTextEdit, QLineEdit {
                background-color: #0f172a;
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                padding: 6px;
            }
        """
        self.recipientCombo.setStyleSheet(input_style)
        self.typeCombo.setStyleSheet(input_style)
        self.countryCombo.setStyleSheet(input_style)
        self.phoneInput.setStyleSheet(input_style)
        self.msgInput.setStyleSheet(input_style)
        
        layout.addRow(QLabel("Send To:"), self.recipientCombo)
        layout.addRow(QLabel("Country Code:"), self.countryCombo)
        layout.addRow(QLabel("Guest Phone Number:"), self.phoneInput)
        layout.addRow(QLabel("Message Type:"), self.typeCombo)
        layout.addRow(QLabel("Message Content:"), self.msgInput)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QPushButton {
                background-color: #25d366; /* WhatsApp Green */
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ebd56;
            }
        """)
        layout.addRow(buttons)
        
    def on_recipient_changed(self):
        data = self.recipientCombo.currentData()
        if data and len(data) >= 4 and data[0] != "All":
            phone = data[3] if data[3] else ""
            self.phoneInput.setText(phone)
        else:
            self.phoneInput.clear()

    def get_data(self):
        recipient_data = self.recipientCombo.currentData()
        selected_country_text = self.countryCombo.currentText()
        prefix = COUNTRY_CODES.get(selected_country_text, "233")
        
        raw_phone = self.phoneInput.text().strip()
        clean_digits = "".join(filter(str.isdigit, raw_phone))
        
        # Automatically clear leading zero if present and prepend selected country code prefix
        if clean_digits.startswith("0"):
            clean_digits = clean_digits[1:]
        
        formatted_phone = prefix + clean_digits if clean_digits else ""
        
        return {
            "recipient_data": recipient_data,
            "msg_type": self.typeCombo.currentText(),
            "phone_number": formatted_phone,
            "content": self.msgInput.toPlainText().strip()
        }

class MessageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apex Horizon Suites - Guest Messages & Communications")
        self.resize(1100, 650)
        
        self.init_message_table()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header Layout
        header_layout = QHBoxLayout()
        
        btnBack = QPushButton("← Dashboard")
        btnBack.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 41, 59, 200);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(51, 65, 85, 220);
            }
        """)
        btnBack.clicked.connect(self.close)
        header_layout.addWidget(btnBack)
        
        title = QLabel("Guest Messages & Communications")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Search message or recipient...")
        self.searchBar.setFixedWidth(240)
        self.searchBar.setStyleSheet("""
            QLineEdit {
                background-color: rgba(30, 41, 59, 200);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                padding: 6px;
            }
        """)
        self.searchBar.textChanged.connect(self.filter_messages)
        header_layout.addWidget(self.searchBar)
        
        btnCompose = QPushButton("+ New Message")
        btnCompose.setStyleSheet("""
            QPushButton {
                background-color: #25d366;
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ebd56;
            }
        """)
        btnCompose.clicked.connect(self.compose_message)
        header_layout.addWidget(btnCompose)
        
        layout.addLayout(header_layout)
        
        # Messages Table
        self.tableMessages = QTableWidget()
        self.tableMessages.setColumnCount(6)
        self.tableMessages.setHorizontalHeaderLabels([
            "ID", "Recipient Name", "Room", "Type", "Message Content", "Timestamp"
        ])
        self.tableMessages.verticalHeader().setDefaultSectionSize(50)
        
        self.tableMessages.setStyleSheet("""
            QTableWidget {
                background-color: rgba(15, 23, 42, 180);
                color: white;
                gridline-color: rgba(255, 255, 255, 20);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: rgba(30, 41, 59, 220);
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid rgba(255, 255, 255, 10);
            }
        """)
        
        header = self.tableMessages.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.load_messages_from_db()
        layout.addWidget(self.tableMessages)
        self.setStyleSheet("QMainWindow { background-color: #0f172a; }")

    def init_message_table(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_id INTEGER,
                recipient_name TEXT,
                room_number TEXT,
                message_text TEXT,
                message_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def load_messages_from_db(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT message_id, recipient_name, room_number, message_type, message_text, timestamp
            FROM Messages
            ORDER BY message_id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        self.populate_table(rows)

    def populate_table(self, data):
        self.tableMessages.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.tableMessages.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
            self.tableMessages.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
            self.tableMessages.setItem(row_idx, 2, QTableWidgetItem(str(row_data[2])))
            
            type_item = QTableWidgetItem(str(row_data[3]))
            type_item.setForeground(Qt.cyan)
            self.tableMessages.setItem(row_idx, 3, type_item)
            
            self.tableMessages.setItem(row_idx, 4, QTableWidgetItem(str(row_data[4])))
            self.tableMessages.setItem(row_idx, 5, QTableWidgetItem(str(row_data[5])))

    def filter_messages(self, text):
        search_text = text.lower()
        for row in range(self.tableMessages.rowCount()):
            match = False
            for col in range(self.tableMessages.columnCount()):
                item = self.tableMessages.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.tableMessages.setRowHidden(row, not match)

    def compose_message(self):
        dialog = ComposeMessageDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["recipient_data"]:
                QMessageBox.warning(self, "Validation Error", "Please select a recipient.")
                return
            if not data["content"]:
                QMessageBox.warning(self, "Validation Error", "Message content cannot be empty.")
                return
                
            conn = get_connection()
            cursor = conn.cursor()
            
            # Check if broadcast
            if data["recipient_data"][0] == "All":
                cursor.execute("""
                    SELECT g.guest_id, g.full_name, b.room_number 
                    FROM Bookings b
                    JOIN Guests g ON b.guest_id = g.guest_id
                    WHERE b.booking_status IN ('Confirmed', 'Checked In')
                """)
                active_guests = cursor.fetchall()
                if not active_guests:
                    QMessageBox.warning(self, "Notice", "No active guests to broadcast to.")
                    conn.close()
                    return
                for g in active_guests:
                    cursor.execute("""
                        INSERT INTO Messages (guest_id, recipient_name, room_number, message_text, message_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (g[0], g[1], g[2], data["content"], data["msg_type"]))
            else:
                g_id, g_name, r_num, _ = data["recipient_data"]
                cursor.execute("""
                    INSERT INTO Messages (guest_id, recipient_name, room_number, message_text, message_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (g_id, g_name, r_num, data["content"], data["msg_type"]))
                
            conn.commit()
            conn.close()
            
            self.load_messages_from_db()
            
            # If WhatsApp option is chosen and phone number is provided, trigger WhatsApp
            if "WhatsApp" in data["msg_type"] and data["phone_number"]:
                encoded_message = urllib.parse.quote(data["content"])
                whatsapp_url = f"https://wa.me/{data['phone_number']}?text={encoded_message}"
                webbrowser.open(whatsapp_url)
                
            QMessageBox.information(self, "Success", "Message saved and WhatsApp launched successfully!")