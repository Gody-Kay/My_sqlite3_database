from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication


def get_color_palette():
    return {
        "background": "#060816",
        "panel": "#111827",
        "panel_alt": "#16213e",
        "border": "#334155",
        "accent": "#60a5fa",
        "accent_alt": "#818cf8",
        "accent_dark": "#2563eb",
        "text": "#f8fafc",
        "muted": "#94a3b8",
        "success": "#34d399",
        "danger": "#fb7185",
    }


def get_app_stylesheet():
    palette = get_color_palette()
    return f"""
        QWidget {{
            color: {palette['text']};
            font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
            background: transparent;
        }}

        QDialog, QMainWindow, QWidget {{
            background-color: {palette['background']};
            color: {palette['text']};
        }}

        QLabel {{
            color: {palette['text']};
            background: transparent;
        }}

        QPushButton, QToolButton {{
            background-color: {palette['panel']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 10px;
            padding: 10px 14px;
            font-weight: 600;
        }}

        QPushButton:hover, QToolButton:hover {{
            background-color: {palette['accent']};
            color: #07111f;
        }}

        QPushButton:pressed, QToolButton:pressed {{
            background-color: {palette['accent_dark']};
            margin-top: 1px;
            margin-left: 1px;
        }}

        QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QComboBox {{
            background-color: {palette['panel_alt']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 8px;
            padding: 8px 10px;
        }}

        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {palette['accent']};
        }}

        QFrame {{
            background-color: transparent;
        }}

        QProgressBar {{
            border: 1px solid {palette['border']};
            border-radius: 8px;
            background-color: #0b1120;
            color: transparent;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {palette['accent']}, stop:1 {palette['accent_alt']});
            border-radius: 8px;
        }}
    """


def apply_global_theme(app: QApplication):
    app.setStyle("Fusion")
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#060816"))
    palette.setColor(QPalette.WindowText, QColor("#f8fafc"))
    palette.setColor(QPalette.Base, QColor("#111827"))
    palette.setColor(QPalette.AlternateBase, QColor("#16213e"))
    palette.setColor(QPalette.ToolTipBase, QColor("#111827"))
    palette.setColor(QPalette.ToolTipText, QColor("#f8fafc"))
    palette.setColor(QPalette.Text, QColor("#f8fafc"))
    palette.setColor(QPalette.Button, QColor("#111827"))
    palette.setColor(QPalette.ButtonText, QColor("#f8fafc"))
    palette.setColor(QPalette.BrightText, QColor("#f8fafc"))
    palette.setColor(QPalette.Highlight, QColor("#60a5fa"))
    palette.setColor(QPalette.HighlightedText, QColor("#07111f"))
    palette.setColor(QPalette.Link, QColor("#818cf8"))
    app.setPalette(palette)
    app.setStyleSheet(get_app_stylesheet())
