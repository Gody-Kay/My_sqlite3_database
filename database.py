import os
import sqlite3
import sys
from pathlib import Path


def get_db_path():
    """Resolve the database path for normal execution and packaged builds."""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent
    return base_path / "database" / "hotel.db"


DB_PATH = str(get_db_path())

def get_connection():
    """Ensures the database directory exists and returns a live connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def initialize_database():
    """Creates all master tables and seeds initial data if the database is empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Employees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employees (
            employee_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            role_department TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    
    # 2. Rooms Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Rooms (
            room_number TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            price_per_night REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)
    
    # 3. Guests Table (Updated with loyalty_status for CRM integration)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Guests (
            guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone_number TEXT,
            email TEXT,
            address TEXT,
            loyalty_status TEXT DEFAULT 'Standard'
        )
    """)
    
    # 4. Bookings Table (Future-proof for reservation management)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT,
            guest_id INTEGER,
            check_in_date TEXT,
            check_out_date TEXT,
            total_amount REAL,
            payment_status TEXT,
            booking_status TEXT,
            FOREIGN KEY (room_number) REFERENCES Rooms(room_number),
            FOREIGN KEY (guest_id) REFERENCES Guests(guest_id)
        )
    """)
    
    # 5. Finance Table (Used for revenue tracking & analytics export)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Finance (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT,
            description TEXT,
            category TEXT,
            amount REAL,
            transaction_type TEXT
        )
    """)
    
    # 6. Messages Table (Used for internal staff notifications/chat)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            recipient TEXT,
            content TEXT,
            timestamp TEXT,
            status TEXT
        )
    """)

    # 7. Users Table (For system login and credentials management)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    conn.commit()
    
    # --- Seed Default Employees if Table is Empty ---
    cursor.execute("SELECT COUNT(*) FROM Employees")
    if cursor.fetchone()[0] == 0:
        default_employees = [
            ("EMP-001", "Kwame Mensah", "Front Desk Supervisor", "+233 24 123 4567", "Active"),
            ("EMP-002", "Abena Osei", "Housekeeping Lead", "+233 20 987 6543", "Active"),
            ("EMP-003", "Kofi Antwi", "Maintenance Technician", "+233 54 555 7890", "On Leave"),
            ("EMP-004", "Akosua Dapaah", "Restaurant Manager", "+233 27 333 2211", "Active")
        ]
        cursor.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?, ?)", default_employees)
        conn.commit()
        
    # --- Seed Default Rooms if Table is Empty ---
    cursor.execute("SELECT COUNT(*) FROM Rooms")
    if cursor.fetchone()[0] == 0:
        default_rooms = []
        for i in range(101, 116):
            default_rooms.append((str(i), "Deluxe Single", 120.0, "Available"))
        for i in range(116, 131):
            default_rooms.append((str(i), "Executive Double", 200.0, "Available"))
        for i in range(201, 211):
            default_rooms.append((str(i), "Luxury Suite", 350.0, "Available"))
        for i in range(211, 221):
            default_rooms.append((str(i), "Standard Twin", 90.0, "Available"))
        cursor.executemany("INSERT INTO Rooms VALUES (?, ?, ?, ?)", default_rooms)
        conn.commit()

    # --- Seed Default Admin User if None Exists ---
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", ("admin", "password123"))
        conn.commit()
        
    conn.close()

def verify_user_credentials(username, password):
    """Checks if the entered username and password match the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def update_user_credentials(old_username, new_username, new_password):
    """Updates the username and password in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Users SET username = ?, password = ? WHERE username = ?", 
                       (new_username, new_password, old_username))
        conn.commit()
        success = cursor.rowcount > 0
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success