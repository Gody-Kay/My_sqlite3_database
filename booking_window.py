import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog, QComboBox, QDateEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate
from database import get_connection

class NewBookingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Booking")
        self.resize(420, 480)
        self.setStyleSheet("background-color: #1e293b; color: white;")
        
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("e.g. Ama Serwaa")
        
        self.phoneInput = QLineEdit()
        self.phoneInput.setPlaceholderText("e.g. +233 24 000 0000")
        
        self.roomCombo = QComboBox()
        
        # PREVENT DOUBLE BOOKING: Only fetch rooms that are currently marked as 'Available'
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT room_number, category, price_per_night FROM Rooms WHERE status = 'Available'")
        self.rooms_data = cursor.fetchall()
        conn.close()
        
        if not self.rooms_data:
            self.roomCombo.addItem("No available rooms found!", None)
            self.roomCombo.setEnabled(False)
        else:
            for r in self.rooms_data:
                self.roomCombo.addItem(f"Room {r[0]} ({r[1]} - GH₵{r[2]:.0f}/night)", r[0])
            
        self.checkInDate = QDateEdit()
        self.checkInDate.setDate(QDate.currentDate())
        self.checkInDate.setCalendarPopup(True)
        
        self.checkOutDate = QDateEdit()
        self.checkOutDate.setDate(QDate.currentDate().addDays(1))
        self.checkOutDate.setCalendarPopup(True)
        
        self.paymentCombo = QComboBox()
        self.paymentCombo.addItems(["Pending", "Paid", "Partial"])
        
        self.statusCombo = QComboBox()
        self.statusCombo.addItems(["Confirmed", "Checked In", "Checked Out", "Cancelled"])
        
        input_style = """
            QLineEdit, QComboBox, QDateEdit {
                background-color: #0f172a;
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                padding: 6px;
            }
        """
        self.nameInput.setStyleSheet(input_style)
        self.phoneInput.setStyleSheet(input_style)
        self.roomCombo.setStyleSheet(input_style)
        self.checkInDate.setStyleSheet(input_style)
        self.checkOutDate.setStyleSheet(input_style)
        self.paymentCombo.setStyleSheet(input_style)
        self.statusCombo.setStyleSheet(input_style)
        
        layout.addRow(QLabel("Guest Full Name:"), self.nameInput)
        layout.addRow(QLabel("Phone Number:"), self.phoneInput)
        layout.addRow(QLabel("Select Room:"), self.roomCombo)
        layout.addRow(QLabel("Check-In Date:"), self.checkInDate)
        layout.addRow(QLabel("Check-Out Date:"), self.checkOutDate)
        layout.addRow(QLabel("Payment Status:"), self.paymentCombo)
        layout.addRow(QLabel("Booking Status:"), self.statusCombo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        layout.addRow(buttons)

    def get_data(self):
        if not self.rooms_data:
            return None
            
        selected_room_idx = self.roomCombo.currentIndex()
        room_num = self.rooms_data[selected_room_idx][0]
        price_per_night = self.rooms_data[selected_room_idx][2]
        
        d_in = self.checkInDate.date().toPyDate()
        d_out = self.checkOutDate.date().toPyDate()
        nights = (d_out - d_in).days
        if nights <= 0:
            nights = 1
        
        total_amount = price_per_night * nights
        
        return {
            "name": self.nameInput.text().strip(),
            "phone": self.phoneInput.text().strip(),
            "room_number": room_num,
            "check_in": d_in.strftime("%Y-%m-%d"),
            "check_out": d_out.strftime("%Y-%m-%d"),
            "total_amount": total_amount,
            "payment_status": self.paymentCombo.currentText(),
            "booking_status": self.statusCombo.currentText()
        }

class BookingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apex Horizon Suites - Bookings & Reservations")
        self.resize(1100, 650)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
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
        
        title = QLabel("Bookings & Reservations")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Search guest or room...")
        self.searchBar.setFixedWidth(220)
        self.searchBar.setStyleSheet("""
            QLineEdit {
                background-color: rgba(30, 41, 59, 200);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                padding: 6px;
            }
        """)
        self.searchBar.textChanged.connect(self.filter_bookings)
        header_layout.addWidget(self.searchBar)
        
        btnAdd = QPushButton("+ New Booking")
        btnAdd.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """)
        btnAdd.clicked.connect(self.add_booking)
        header_layout.addWidget(btnAdd)
        
        btnDelete = QPushButton("Delete Booking")
        btnDelete.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btnDelete.clicked.connect(self.delete_booking)
        header_layout.addWidget(btnDelete)
        
        layout.addLayout(header_layout)
        
        self.tableBookings = QTableWidget()
        self.tableBookings.setColumnCount(8)
        self.tableBookings.setHorizontalHeaderLabels([
            "ID", "Guest Name", "Phone", "Room", "Check-In", "Check-Out", "Total (GH₵)", "Status"
        ])
        self.tableBookings.verticalHeader().setDefaultSectionSize(50)
        
        self.tableBookings.setStyleSheet("""
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
        
        header = self.tableBookings.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.tableBookings.setColumnWidth(7, 160)
        
        self.load_bookings_from_db()
        layout.addWidget(self.tableBookings)
        self.setStyleSheet("QMainWindow { background-color: #0f172a; }")

    def load_bookings_from_db(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.booking_id, g.full_name, g.phone_number, b.room_number, 
                   b.check_in_date, b.check_out_date, b.total_amount, b.booking_status
            FROM Bookings b
            JOIN Guests g ON b.guest_id = g.guest_id
            ORDER BY b.booking_id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        self.populate_table(rows)

    def populate_table(self, data):
        self.tableBookings.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.tableBookings.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
            self.tableBookings.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
            self.tableBookings.setItem(row_idx, 2, QTableWidgetItem(str(row_data[2])))
            self.tableBookings.setItem(row_idx, 3, QTableWidgetItem(str(row_data[3])))
            self.tableBookings.setItem(row_idx, 4, QTableWidgetItem(str(row_data[4])))
            self.tableBookings.setItem(row_idx, 5, QTableWidgetItem(str(row_data[5])))
            self.tableBookings.setItem(row_idx, 6, QTableWidgetItem(f"GH₵{row_data[6]:.2f}"))
            
            status_combo = QComboBox()
            status_combo.addItems(["Confirmed", "Checked In", "Checked Out", "Cancelled"])
            status_combo.setCurrentText(str(row_data[7]))
            
            b_id = row_data[0]
            status_combo.currentTextChanged.connect(lambda text, booking_id=b_id: self.update_booking_status_db(booking_id, text))
            
            status_combo.setStyleSheet("""
                QComboBox {
                    background-color: #1e293b;
                    color: #ffffff;
                    padding: 6px 10px;
                    border: 1px solid rgba(255, 255, 255, 50);
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 24px;
                    border-left-width: 0px;
                }
                QComboBox QAbstractItemView {
                    background-color: #1e293b;
                    color: #ffffff;
                    selection-background-color: #3b82f6;
                    selection-color: #ffffff;
                    padding: 4px;
                }
            """)
            self.tableBookings.setCellWidget(row_idx, 7, status_combo)

    def update_booking_status_db(self, booking_id, new_status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Bookings SET booking_status = ? WHERE booking_id = ?", (new_status, booking_id))
        
        cursor.execute("SELECT room_number FROM Bookings WHERE booking_id = ?", (booking_id,))
        res = cursor.fetchone()
        if res:
            room_num = res[0]
            if new_status == "Checked In":
                cursor.execute("UPDATE Rooms SET status = 'Occupied' WHERE room_number = ?", (room_num,))
            elif new_status == "Confirmed":
                cursor.execute("UPDATE Rooms SET status = 'Reserved' WHERE room_number = ?", (room_num,))
            elif new_status in ["Checked Out", "Cancelled"]:
                cursor.execute("UPDATE Rooms SET status = 'Available' WHERE room_number = ?", (room_num,))
                
        conn.commit()
        conn.close()

    def filter_bookings(self, text):
        search_text = text.lower()
        for row in range(self.tableBookings.rowCount()):
            match = False
            for col in range(self.tableBookings.columnCount()):
                item = self.tableBookings.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            combo = self.tableBookings.cellWidget(row, 7)
            if combo and search_text in combo.currentText().lower():
                match = True
                
            self.tableBookings.setRowHidden(row, not match)

    def add_booking(self):
        dialog = NewBookingDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data or not data["name"]:
                QMessageBox.warning(self, "Validation Error", "Guest name cannot be empty or no rooms are available.")
                return
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO Guests (full_name, phone_number) VALUES (?, ?)",
                (data["name"], data["phone"])
            )
            guest_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO Bookings (room_number, guest_id, check_in_date, check_out_date, total_amount, payment_status, booking_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["room_number"], guest_id, data["check_in"], data["check_out"],
                data["total_amount"], data["payment_status"], data["booking_status"]
            ))
            
            # Automatically update room status to 'Reserved' or 'Occupied' so it's locked out from other bookings
            room_status = "Reserved"
            if data["booking_status"] == "Checked In":
                room_status = "Occupied"
            cursor.execute("UPDATE Rooms SET status = ? WHERE room_number = ?", (room_status, data["room_number"]))
            
            conn.commit()
            conn.close()
            
            self.load_bookings_from_db()
            self.filter_bookings(self.searchBar.text())
            QMessageBox.information(self, "Success", "Booking created and room status locked successfully!")

    def delete_booking(self):
        selected_row = self.tableBookings.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a booking row to delete.")
            return
        
        b_id_item = self.tableBookings.item(selected_row, 0)
        if b_id_item:
            b_id = b_id_item.text()
            confirm = QMessageBox.question(self, "Confirm Deletion", f"Delete booking ID {b_id} and free up the room?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Free up the room back to 'Available' when booking is deleted
                cursor.execute("SELECT room_number FROM Bookings WHERE booking_id = ?", (b_id,))
                res = cursor.fetchone()
                if res:
                    cursor.execute("UPDATE Rooms SET status = 'Available' WHERE room_number = ?", (res[0],))
                    
                cursor.execute("DELETE FROM Bookings WHERE booking_id = ?", (b_id,))
                conn.commit()
                conn.close()
                
                self.load_bookings_from_db()
                self.filter_bookings(self.searchBar.text())