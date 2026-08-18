import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QToolButton,
                             QGraphicsOpacityEffect, QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QWidget, QFrame,
                             QGraphicsDropShadowEffect, QProgressBar)
from PyQt5.QtCore import QObject, QEvent, QPropertyAnimation, QRect, QEasingCurve, Qt, QTimer
from PyQt5.QtGui import QColor, QPixmap
from PyQt5 import uic

from database import initialize_database, update_user_credentials, get_connection
from login_window import LoginWindow
from theme import apply_global_theme, get_app_stylesheet

from employee_window import EmployeeWindow
from room_window import RoomWindow
from booking_window import BookingWindow
from finance_window import FinanceWindow
from message_window import MessageWindow

# --- Newly Integrated Modules ---
# from housekeeping import HousekeepingWindow
# from crm import GuestCRMWindow
# from analytics import AnalyticsExportWindow
# from messaging import MessagingWindow


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    candidates = [
        base_path / relative_path,
        base_path.parent / relative_path,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


class SplashScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hotel Manager")
        self.setFixedSize(480, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(get_app_stylesheet())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setObjectName("splashCard")
        card.setStyleSheet("""
            QFrame#splashCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:1 #111827);
                border: 1px solid #334155;
                border-radius: 24px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(16)

        title = QLabel("Hotel Manager")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #f8fafc;")
        card_layout.addWidget(title)

        subtitle = QLabel("Preparing a polished experience for your team...")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #94a3b8;")
        card_layout.addWidget(subtitle)

        progress = QProgressBar(self)
        progress.setRange(0, 0)
        progress.setFixedHeight(8)
        progress.setTextVisible(False)
        card_layout.addWidget(progress)

        footer = QLabel("Launching secure operations dashboard")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 12px; color: #60a5fa;")
        card_layout.addWidget(footer)

        layout.addWidget(card)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        card.setGraphicsEffect(shadow)

        QTimer.singleShot(1400, self.accept)


class ChangeCredentialsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Login Credentials")
        self.setFixedSize(420, 320)
        self.setStyleSheet(get_app_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Current Username:"))
        self.old_user_input = QLineEdit(self)
        layout.addWidget(self.old_user_input)

        layout.addWidget(QLabel("New Username:"))
        self.new_user_input = QLineEdit(self)
        layout.addWidget(self.new_user_input)

        layout.addWidget(QLabel("New Password:"))
        self.new_pass_input = QLineEdit(self)
        self.new_pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_pass_input)

        self.save_btn = QPushButton("Save Changes", self)
        self.save_btn.clicked.connect(self.save_credentials)
        layout.addWidget(self.save_btn)

    def save_credentials(self):
        old_user = self.old_user_input.text().strip()
        new_user = self.new_user_input.text().strip()
        new_pass = self.new_pass_input.text().strip()

        if not old_user or not new_user or not new_pass:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        success = update_user_credentials(old_user, new_user, new_pass)
        if success:
            QMessageBox.information(self, "Success", "Credentials updated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update. Check your current username or try a different new username.")


class HotelDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = get_resource_path("home_dashboard.ui")
        uic.loadUi(str(ui_path), self)
        
        self.active_windows = []
        
        # Window Registry updated with new modules
        self.window_registry = {
            'btnEmployees': EmployeeWindow,
            'btnRooms': RoomWindow,
            'btnRoomManagement': RoomWindow,
            'btnBookings': BookingWindow,
            'btnFinance': FinanceWindow,
            'btnMessages': MessageWindow,
            # 'btnHousekeeping': HousekeepingWindow,
            # 'btnCRM': GuestCRMWindow,
            # 'btnAnalytics': AnalyticsExportWindow,
            # 'btnInternalMessages': MessagingWindow,
        }
        
        for btn_name, window_class in self.window_registry.items():
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                btn.clicked.connect(lambda checked, cls=window_class: self.open_window(cls))

        # Setup Sidebar Fade Animation & Initial Hidden State
        if hasattr(self, 'sidebarFrame'):
            self.sidebar_opacity_effect = QGraphicsOpacityEffect(self.sidebarFrame)
            self.sidebarFrame.setGraphicsEffect(self.sidebar_opacity_effect)
            self.sidebar_opacity_effect.setOpacity(0.0)
            self.sidebarFrame.setVisible(False)
            
            if hasattr(self, 'btnSettings'):
                self.btnSettings.setVisible(False)
                
            self.sidebar_is_open = False
            
            self.sidebar_anim = QPropertyAnimation(self.sidebar_opacity_effect, b"opacity")
            self.sidebar_anim.setDuration(180)
            self.sidebar_anim.setEasingCurve(QEasingCurve.OutCubic)
            self.sidebarFrame.raise_()

        if hasattr(self, 'btnSettings'):
            self.btnSettings.setEnabled(True)
            self.btnSettings.raise_()
            self.btnSettings.clicked.connect(self.open_settings_dialog)

        # --- Cinematic Background Crossfade Setup (45s Interval) ---
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(self.rect())
        self.bg_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.bg_label.setAlignment(Qt.AlignCenter)
        self.bg_label.setStyleSheet("background-color: #060816;")
        self.bg_label.lower()

        self.bg_overlay = QLabel(self)
        self.bg_overlay.setGeometry(self.rect())
        self.bg_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.bg_overlay.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(6, 8, 22, 0.10), stop:1 rgba(15, 23, 42, 0.75));")
        self.bg_overlay.lower()

        self.bg_opacity = QGraphicsOpacityEffect(self.bg_label)
        self.bg_label.setGraphicsEffect(self.bg_opacity)
        self.bg_opacity.setOpacity(1.0)

        self.bg_anim = QPropertyAnimation(self.bg_opacity, b"opacity")
        self.bg_anim.setDuration(1200)
        self.bg_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.wallpaper_list = self.discover_wallpapers()
        self.current_wallpaper_index = 0
        self.current_wallpaper_path = None

        if self.wallpaper_list:
            self.rotate_wallpaper()
            self.wallpaper_timer = QTimer(self)
            self.wallpaper_timer.timeout.connect(self.rotate_wallpaper)
            self.wallpaper_timer.start(45000)
        else:
            self.apply_fallback_background()

        # --- Live Analytics & Very Big Numeric Clock Cards (Pinned to Top-Right) ---
        self.init_dashboard_cards()
        
        # Clock Timer (Updates every 1 second)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_live_clock)
        self.clock_timer.start(1000)
        self.update_live_clock()

        # Periodic Live Data Refresh Timer (Updates metrics every 5 seconds)
        self.live_timer = QTimer(self)
        self.live_timer.timeout.connect(self.load_dashboard_metrics)
        self.live_timer.start(5000)
        self.load_dashboard_metrics()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg_label'):
            self.bg_label.setGeometry(self.rect())
        if hasattr(self, 'bg_overlay'):
            self.bg_overlay.setGeometry(self.rect())
        if hasattr(self, 'metrics_wrapper'):
            self.metrics_wrapper.setGeometry(self.width() - 1065, 20, 1040, 100)
        if hasattr(self, 'current_wallpaper_path') and self.current_wallpaper_path:
            self.apply_wallpaper(self.current_wallpaper_path)

    def discover_wallpapers(self):
        images_dir = get_resource_path("images")
        valid_extensions = (".jpg", ".jpeg", ".png", ".webp")
        if not images_dir.exists():
            return []
        return [str(p) for p in sorted(images_dir.iterdir()) if p.suffix.lower() in valid_extensions]

    def apply_fallback_background(self):
        self.bg_label.setPixmap(QPixmap())
        self.bg_label.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:1 #111827);")

    def apply_wallpaper(self, image_path):
        self.current_wallpaper_path = image_path
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.apply_fallback_background()
            return

        scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.bg_label.setStyleSheet("background: transparent;")
        self.bg_label.setPixmap(scaled)
        self.bg_label.setAlignment(Qt.AlignCenter)

    def rotate_wallpaper(self):
        if not self.wallpaper_list:
            self.apply_fallback_background()
            return

        image_path = self.wallpaper_list[self.current_wallpaper_index].replace("\\", "/")
        self.current_wallpaper_index = (self.current_wallpaper_index + 1) % len(self.wallpaper_list)

        self.apply_wallpaper(image_path)
        self.bg_opacity.setOpacity(1.0)

    def init_dashboard_cards(self):
        self.metrics_wrapper = QWidget(self)
        self.metrics_wrapper.setGeometry(self.width() - 1065, 20, 1040, 100)
        
        layout = QHBoxLayout(self.metrics_wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.create_clock_card(layout)

        self.lbl_room_metric = self.create_card(layout, "🛏️ Available Rooms", "0")
        self.lbl_emp_metric = self.create_card(layout, "👥 Active Staff", "0")
        self.lbl_rev_metric = self.create_card(layout, "💰 Total Revenue", "$0.0")

    def create_clock_card(self, parent_layout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 140);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
            }
        """)
        
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(16, 8, 16, 8)
        vbox.setSpacing(0)

        self.time_lbl = QLabel("00:00:00")
        self.time_lbl.setAlignment(Qt.AlignCenter)
        self.time_lbl.setStyleSheet("""
            color: #ffffff; 
            font-size: 50px; 
            font-weight: bold; 
            background: transparent; 
            border: none;
            letter-spacing: 2px;
        """)
        vbox.addWidget(self.time_lbl)

        self.date_lbl = QLabel("0000-00-00")
        self.date_lbl.setAlignment(Qt.AlignCenter)
        self.date_lbl.setStyleSheet("""
            color: #38bdf8; 
            font-size: 20px; 
            font-weight: bold; 
            background: transparent; 
            border: none;
        """)
        vbox.addWidget(self.date_lbl)

        parent_layout.addWidget(card)

    def update_live_clock(self):
        if hasattr(self, 'time_lbl') and hasattr(self, 'date_lbl'):
            now = datetime.now()
            self.time_lbl.setText(now.strftime("%H:%M:%S"))
            self.date_lbl.setText(now.strftime("%Y-%m-%d"))

    def create_card(self, parent_layout, title_text, initial_value):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 210);
                border: 1px solid rgba(100, 116, 139, 0.5);
                border-radius: 20px;
            }
        """)
        
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(4)

        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        vbox.addWidget(title_lbl)

        val_lbl = QLabel(initial_value)
        val_lbl.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; background: transparent; border: none;")
        vbox.addWidget(val_lbl)

        parent_layout.addWidget(card)
        return val_lbl

    def load_dashboard_metrics(self):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM Rooms WHERE status = 'Available'")
            res_rooms = cursor.fetchone()
            if res_rooms and hasattr(self, 'lbl_room_metric'):
                self.lbl_room_metric.setText(str(res_rooms[0]))
                
            cursor.execute("SELECT COUNT(*) FROM Employees WHERE status = 'Active'")
            res_emp = cursor.fetchone()
            if res_emp and hasattr(self, 'lbl_emp_metric'):
                self.lbl_emp_metric.setText(str(res_emp[0]))

            cursor.execute("SELECT SUM(amount) FROM Finance WHERE transaction_type = 'Income'")
            res_rev = cursor.fetchone()
            total_rev = res_rev[0] if res_rev and res_rev[0] is not None else 0.0
            if hasattr(self, 'lbl_rev_metric'):
                self.lbl_rev_metric.setText(f"${total_rev:,.2f}")
        except Exception:
            pass
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def open_settings_dialog(self):
        dialog = ChangeCredentialsDialog(self)
        dialog.exec_()

    def mousePressEvent(self, event):
        if hasattr(self, 'sidebarFrame'):
            pos = event.pos()
            if self.sidebar_is_open:
                in_sidebar = self.sidebarFrame.geometry().contains(pos)
                in_settings = hasattr(self, 'btnSettings') and self.btnSettings.isVisible() and self.btnSettings.underMouse()
                if in_sidebar or in_settings:
                    super().mousePressEvent(event)
                    return
            
            self.toggle_menu_bar()
        super().mousePressEvent(event)

    def toggle_menu_bar(self):
        if hasattr(self, 'sidebarFrame'):
            self.sidebar_anim.stop()
            try:
                self.sidebar_anim.finished.disconnect()
            except Exception:
                pass

            if self.sidebar_is_open:
                self.sidebar_anim.setStartValue(1.0)
                self.sidebar_anim.setEndValue(0.0)
                
                def hide_all():
                    self.sidebarFrame.setVisible(False)
                    if hasattr(self, 'btnSettings'):
                        self.btnSettings.setVisible(False)
                        
                self.sidebar_anim.finished.connect(hide_all)
                self.sidebar_is_open = False
            else:
                self.sidebarFrame.setVisible(True)
                if hasattr(self, 'btnSettings'):
                    self.btnSettings.setVisible(True)
                    self.btnSettings.raise_()
                    
                self.sidebar_anim.setStartValue(0.0)
                self.sidebar_anim.setEndValue(1.0)
                self.sidebar_is_open = True
                
            self.sidebar_anim.start()

    def open_window(self, window_class):
        window = window_class()
        window.showMaximized()
        
        central = window.centralWidget()
        if central:
            opacity_effect = QGraphicsOpacityEffect(central)
            central.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(0.0)
            
            fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
            fade_anim.setDuration(220)
            fade_anim.setStartValue(0.0)
            fade_anim.setEndValue(1.0)
            fade_anim.setEasingCurve(QEasingCurve.OutCubic)
            fade_anim.start()
            
            self.active_windows.append((window, opacity_effect, fade_anim))
        else:
            self.active_windows.append(window)

if __name__ == "__main__":
    initialize_database()
    
    app = QApplication(sys.argv)
    apply_global_theme(app)

    splash = SplashScreen()
    splash.exec_()

    login = LoginWindow()
    if login.exec_() == QDialog.Accepted and login.authenticated:
        window = HotelDashboard()
        window.showMaximized()
        sys.exit(app.exec_())
    else:
        sys.exit(0)