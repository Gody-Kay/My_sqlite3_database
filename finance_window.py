import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QComboBox, QDialog, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from database import get_connection

class ReceiptDialog(QDialog):
    def __init__(self, booking_id, parent=None):
        super().__init__(parent)
        self.b_id = booking_id
        self.setWindowTitle(f"Invoice & Receipt - #AH-{self.b_id:04d}")
        self.resize(480, 600)
        self.setStyleSheet("background-color: #1e293b; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Fetch booking and guest details
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.booking_id, g.full_name, g.phone_number, b.room_number, 
                   b.check_in_date, b.check_out_date, b.total_amount, 
                   b.payment_status, b.booking_status
            FROM Bookings b
            JOIN Guests g ON b.guest_id = g.guest_id
            WHERE b.booking_id = ?
        """, (booking_id,))
        data = cursor.fetchone()
        conn.close()
        
        if not data:
            QMessageBox.warning(self, "Error", "Receipt data not found.")
            self.reject()
            return
            
        self.b_id, self.name, self.phone, self.room, self.check_in, self.check_out, self.total, self.pay_status, self.book_status = data
        
        # Receipt Header
        header_label = QLabel("APEX HORIZON SUITES")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        sub_header = QLabel("Official Statement of Account & Receipt")
        sub_header.setStyleSheet("font-size: 12px; color: #94a3b8; margin-bottom: 10px;")
        sub_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_header)
        
        # Receipt Details Box
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        form_layout = QVBoxLayout(details_frame)
        form_layout.setSpacing(8)
        
        def add_row(label, value):
            row_layout = QHBoxLayout()
            lbl_key = QLabel(label)
            lbl_key.setStyleSheet("color: #94a3b8; font-weight: bold;")
            lbl_val = QLabel(str(value))
            lbl_val.setStyleSheet("color: white;")
            lbl_val.setAlignment(Qt.AlignRight)
            row_layout.addWidget(lbl_key)
            row_layout.addStretch()
            row_layout.addWidget(lbl_val)
            form_layout.addLayout(row_layout)
            
        add_row("Receipt Number:", f"#AH-{self.b_id:04d}")
        add_row("Guest Name:", self.name)
        add_row("Phone Number:", self.phone or "N/A")
        add_row("Room Assigned:", f"Room {self.room}")
        add_row("Check-In Date:", self.check_in)
        add_row("Check-Out Date:", self.check_out)
        add_row("Payment Status:", self.pay_status)
        add_row("Booking Status:", self.book_status)
        
        layout.addWidget(details_frame)
        
        # Total Amount Box
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background-color: #2563eb;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        lbl_total_title = QLabel("TOTAL AMOUNT:")
        lbl_total_title.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        lbl_total_val = QLabel(f"GH₵{self.total:.2f}")
        lbl_total_val.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        total_layout.addWidget(lbl_total_title)
        total_layout.addStretch()
        total_layout.addWidget(lbl_total_val)
        layout.addWidget(total_frame)
        
        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        
        btn_print = QPushButton("🖨️ Print / Save PDF")
        btn_print.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_print.clicked.connect(self.print_receipt)
        btn_layout.addWidget(btn_print)
        
        btn_close = QPushButton("Close")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: white;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)

    def print_receipt(self):
        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        
        if print_dialog.exec_() == QPrintDialog.Accepted:
            html_content = f"""
            <div style="font-family: Arial, sans-serif; padding: 30px; max-width: 450px; margin: auto; border: 2px solid #1e293b; border-radius: 10px;">
                <h2 style="text-align: center; color: #1e293b; margin-bottom: 5px;">APEX HORIZON SUITES</h2>
                <p style="text-align: center; color: #64748b; font-size: 12px; margin-top: 0;">Official Statement of Account & Receipt</p>
                <hr style="border: 0; border-top: 1px solid #cbd5e1; margin: 20px 0;">
                
                <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
                    <tr><td style="color: #64748b; padding: 6px 0;"><b>Receipt Number:</b></td><td style="text-align: right; padding: 6px 0;">#AH-{self.b_id:04d}</td></tr>
                    <tr><td style="color: #64748b; padding: 6px 0;"><b>Guest Name:</b></td><td style="text-align: right; padding: 6px 0;">{self.name}</td></tr>
                    <tr><td style="color: #64748b; padding: 6px 0;"><b>Phone Number:</b></td><td style="text-align: right; padding: 6px 0;">{self.phone or 'N/A'}</td></tr>
                    <tr><td style="color: #64748b; padding: 6px 0;"><b>Room Assigned:</b></td><td style="text-align: right; padding: 6px 0;">Room {self.room}</td></tr>
                    <tr><td style="color: #64748b; padding: 6px 0;"><b>Check-In Date:</b></td><td style="text-align: right; padding: 6px 0;">{self.check_in}</td></tr>
                    <tr><td style="color: #64748b; padding: 6px 0;"><b>Check-Out Date:</b></td><td style="text-align: right; padding: 6px 0;">{self.check_out}</td></tr>
                    <tr><td style="color: #64748b; padding: 6px 0;"><b>Payment Status:</b></td><td style="text-align: right; padding: 6px 0;">{self.pay_status}</td></tr>
                    <tr><td style="color: #64748b; padding: 6px 0;"><b>Booking Status:</b></td><td style="text-align: right; padding: 6px 0;">{self.book_status}</td></tr>
                </table>
                
                <hr style="border: 0; border-top: 1px solid #cbd5e1; margin: 20px 0;">
                
                <div style="background-color: #f1f5f9; padding: 12px; border-radius: 6px; text-align: right;">
                    <span style="font-size: 14px; font-weight: bold; color: #0f172a;">TOTAL AMOUNT: </span>
                    <span style="font-size: 18px; font-weight: bold; color: #2563eb;">GH₵{self.total:.2f}</span>
                </div>
                
                <p style="text-align: center; font-size: 11px; color: #94a3b8; margin-top: 40px;">
                    Thank you for staying with Apex Horizon Suites!<br>
                    <i>This is a computer-generated official document.</i>
                </p>
            </div>
            """
            document = QTextDocument()
            document.setHtml(html_content)
            document.print_(printer)
            QMessageBox.information(self, "Success", "Receipt sent to printer successfully!")

class FinanceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apex Horizon Suites - Finance & Receipts")
        self.resize(1150, 680)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Top Header Bar
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
        
        title = QLabel("Finance & Receipts")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Filter Dropdown
        self.filterCombo = QComboBox()
        self.filterCombo.addItems(["All Payments", "Paid", "Pending", "Partial"])
        self.filterCombo.setFixedWidth(160)
        self.filterCombo.setStyleSheet("""
            QComboBox {
                background-color: rgba(30, 41, 59, 200);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            QComboBox QAbstractItemView {
                background-color: #1e293b;
                color: white;
            }
        """)
        self.filterCombo.currentTextChanged.connect(self.load_financial_data)
        header_layout.addWidget(self.filterCombo)
        
        layout.addLayout(header_layout)
        
        # Metrics Cards Layout
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        self.cardTotal = self.create_metric_card("Total Bookings Value", "GH₵0.00", "#3b82f6")
        self.cardCollected = self.create_metric_card("Collected Revenue (Paid)", "GH₵0.00", "#10b981")
        self.cardPending = self.create_metric_card("Pending Payments", "GH₵0.00", "#f59e0b")
        
        metrics_layout.addWidget(self.cardTotal)
        metrics_layout.addWidget(self.cardCollected)
        metrics_layout.addWidget(self.cardPending)
        layout.addLayout(metrics_layout)
        
        # Transactions Table
        self.tableFinance = QTableWidget()
        self.tableFinance.setColumnCount(8)
        self.tableFinance.setHorizontalHeaderLabels([
            "ID", "Guest Name", "Room", "Check-In", "Check-Out", "Amount (GH₵)", "Payment Status", "Action"
        ])
        self.tableFinance.verticalHeader().setDefaultSectionSize(50)
        
        self.tableFinance.setStyleSheet("""
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
        
        header = self.tableFinance.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.tableFinance.setColumnWidth(7, 140)
        
        self.load_financial_data()
        layout.addWidget(self.tableFinance)
        self.setStyleSheet("QMainWindow { background-color: #0f172a; }")

    def create_metric_card(self, title, value, border_color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(30, 41, 59, 180);
                border-left: 5px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(12, 8, 12, 8)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; border: none;")
        
        lbl_val = QLabel(value)
        lbl_val.setObjectName("valueLabel")
        lbl_val.setStyleSheet("color: white; font-size: 20px; font-weight: bold; border: none;")
        
        vbox.addWidget(lbl_title)
        vbox.addWidget(lbl_val)
        return frame

    def update_metric_card_value(self, card, new_value):
        lbl = card.findChild(QLabel, "valueLabel")
        if lbl:
            lbl.setText(new_value)

    def load_financial_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(total_amount) FROM Bookings")
        total_rev = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(total_amount) FROM Bookings WHERE payment_status = 'Paid'")
        paid_rev = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(total_amount) FROM Bookings WHERE payment_status IN ('Pending', 'Partial')")
        pending_rev = cursor.fetchone()[0] or 0.0
        
        self.update_metric_card_value(self.cardTotal, f"GH₵{total_rev:.2f}")
        self.update_metric_card_value(self.cardCollected, f"GH₵{paid_rev:.2f}")
        self.update_metric_card_value(self.cardPending, f"GH₵{pending_rev:.2f}")
        
        filter_status = self.filterCombo.currentText()
        if filter_status == "All Payments":
            cursor.execute("""
                SELECT b.booking_id, g.full_name, b.room_number, b.check_in_date, 
                       b.check_out_date, b.total_amount, b.payment_status
                FROM Bookings b
                JOIN Guests g ON b.guest_id = g.guest_id
                ORDER BY b.booking_id DESC
            """)
        else:
            cursor.execute("""
                SELECT b.booking_id, g.full_name, b.room_number, b.check_in_date, 
                       b.check_out_date, b.total_amount, b.payment_status
                FROM Bookings b
                JOIN Guests g ON b.guest_id = g.guest_id
                WHERE b.payment_status = ?
                ORDER BY b.booking_id DESC
            """, (filter_status,))
            
        rows = cursor.fetchall()
        conn.close()
        
        self.populate_table(rows)

    def populate_table(self, data):
        self.tableFinance.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.tableFinance.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
            self.tableFinance.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
            self.tableFinance.setItem(row_idx, 2, QTableWidgetItem(str(row_data[2])))
            self.tableFinance.setItem(row_idx, 3, QTableWidgetItem(str(row_data[3])))
            self.tableFinance.setItem(row_idx, 4, QTableWidgetItem(str(row_data[4])))
            self.tableFinance.setItem(row_idx, 5, QTableWidgetItem(f"GH₵{row_data[5]:.2f}"))
            
            status_item = QTableWidgetItem(str(row_data[6]))
            if row_data[6] == "Paid":
                status_item.setForeground(Qt.green)
            elif row_data[6] == "Pending":
                status_item.setForeground(Qt.yellow)
            else:
                status_item.setForeground(Qt.cyan)
            self.tableFinance.setItem(row_idx, 6, status_item)
            
            btn_receipt = QPushButton("View Receipt")
            b_id = row_data[0]
            btn_receipt.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            btn_receipt.clicked.connect(lambda checked, booking_id=b_id: self.open_receipt(booking_id))
            self.tableFinance.setCellWidget(row_idx, 7, btn_receipt)

    def open_receipt(self, booking_id):
        dialog = ReceiptDialog(booking_id, self)
        dialog.exec_()