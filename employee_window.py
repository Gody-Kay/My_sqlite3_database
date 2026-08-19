import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog, QComboBox
)
from PyQt5.QtCore import Qt
from database import get_connection

class EmployeeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apex Horizon Suites - Employee Management")
        self.resize(1000, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header & Action Bar Layout
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
        
        title = QLabel("Employee Management")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Search employee...")
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
        self.searchBar.textChanged.connect(self.filter_employees)
        header_layout.addWidget(self.searchBar)
        
        btnAdd = QPushButton("+ Add Employee")
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
        btnAdd.clicked.connect(self.add_employee)
        header_layout.addWidget(btnAdd)
        
        btnDelete = QPushButton("Delete Selected")
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
        btnDelete.clicked.connect(self.delete_employee)
        header_layout.addWidget(btnDelete)
        
        layout.addLayout(header_layout)
        
        self.tableEmployees = QTableWidget()
        self.tableEmployees.setColumnCount(5)
        self.tableEmployees.setHorizontalHeaderLabels(["Employee ID", "Full Name", "Role / Department", "Phone Number", "Status"])
        self.tableEmployees.verticalHeader().setDefaultSectionSize(50)
        
        self.tableEmployees.setStyleSheet("""
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
        
        header = self.tableEmployees.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.tableEmployees.setColumnWidth(4, 160)
        
        self.load_employees_from_db()
        layout.addWidget(self.tableEmployees)
        self.setStyleSheet("QMainWindow { background-color: #0f172a; }")

    def load_employees_from_db(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id, full_name, role_department, phone_number, status FROM Employees ORDER BY employee_id ASC")
        rows = cursor.fetchall()
        conn.close()
        self.populate_table(rows)

    def populate_table(self, data):
        self.tableEmployees.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.tableEmployees.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
            self.tableEmployees.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
            self.tableEmployees.setItem(row_idx, 2, QTableWidgetItem(str(row_data[2])))
            self.tableEmployees.setItem(row_idx, 3, QTableWidgetItem(str(row_data[3])))
            
            status_combo = QComboBox()
            status_combo.addItems(["Active", "On Leave", "Not Active", "Suspended"])
            status_combo.setCurrentText(str(row_data[4]))
            
            emp_id = str(row_data[0])
            status_combo.currentTextChanged.connect(lambda text, e_id=emp_id: self.update_employee_status_db(e_id, text))
            
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
            self.tableEmployees.setCellWidget(row_idx, 4, status_combo)

    def update_employee_status_db(self, emp_id, new_status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Employees SET status = ? WHERE employee_id = ?", (new_status, emp_id))
        conn.commit()
        conn.close()

    def filter_employees(self, text):
        search_text = text.lower()
        for row in range(self.tableEmployees.rowCount()):
            match = False
            for col in range(self.tableEmployees.columnCount()):
                item = self.tableEmployees.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            combo = self.tableEmployees.cellWidget(row, 4)
            if combo and search_text in combo.currentText().lower():
                match = True
                
            self.tableEmployees.setRowHidden(row, not match)

    def add_employee(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id FROM Employees")
        existing_ids = cursor.fetchall()
        conn.close()

        max_num = 0
        for emp in existing_ids:
            try:
                num = int(emp[0].split("-")[-1])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
        auto_id = f"EMP-{max_num + 1:03d}"

        name, ok1 = QInputDialog.getText(self, "Add Employee", f"Auto ID Generated: {auto_id}\nEnter Full Name:")
        if not ok1 or not name.strip(): return
        
        role, ok2 = QInputDialog.getText(self, "Add Employee", "Enter Role / Department:")
        if not ok2 or not role.strip(): return
        
        phone, ok3 = QInputDialog.getText(self, "Add Employee", "Enter Phone Number:")
        if not ok3 or not phone.strip(): return
        
        statuses = ["Active", "On Leave", "Not Active", "Suspended"]
        status, ok4 = QInputDialog.getItem(self, "Select Status", "Select Employee Status:", statuses, 0, False)
        if not ok4: return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Employees VALUES (?, ?, ?, ?, ?)", (auto_id, name.strip(), role.strip(), phone.strip(), status))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", f"Employee ID {auto_id} already exists.")
            return

        self.load_employees_from_db()
        self.filter_employees(self.searchBar.text())

    def delete_employee(self):
        selected_row = self.tableEmployees.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an employee row to delete.")
            return
        
        emp_id_item = self.tableEmployees.item(selected_row, 0)
        if emp_id_item:
            emp_id = emp_id_item.text()
            confirm = QMessageBox.question(self, "Confirm Deletion", f"Delete employee {emp_id}?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Employees WHERE employee_id = ?", (emp_id,))
                conn.commit()
                conn.close()
                self.load_employees_from_db()
                self.filter_employees(self.searchBar.text())