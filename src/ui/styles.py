from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPalette, QFont, QFontDatabase

def get_stylesheet(theme, font_family, font_size):
    fs = font_size
    t = theme
    return f"""
    QWidget {{
        font-family: "{font_family}";
        font-size: {fs}px;
        color: {t['text']};
        /* 全局 background 改为 transparent,避免级联到所有 descendant widget 时
           把 container 的 border-radius 圆角遮盖。container 自身的 background
           由 QWidget#mainContainer 规则显式设置,不受影响。 */
        background: transparent;
        outline: none;
        border: none;
    }}
    
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {t['scrollbar']};
        border-radius: 3px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QLineEdit {{
    background: {t['input_bg']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 6px 10px;
    color: {t['text']};
}}
QLineEdit:focus {{
    border: 2px solid {t['accent']};
    border-radius: 8px;
    padding: 5px 9px;
}}
    
    QLineEdit {{
    background: {t['input_bg']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 6px 10px;
    color: {t['text']};
}}
QLineEdit:focus {{
    border: 2px solid {t['accent']};
    border-radius: 8px;
    outline: none;
}}
    
    QComboBox {{
        background: {t['input_bg']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        padding: 4px 8px;
        color: {t['text']};
        min-width: 80px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background: {t['card']};
        color: {t['text']};
        border: 1px solid {t['border']};
        selection-background-color: {t['accent']};
    }}
    
    QPushButton {{
        background: {t['button_bg']};
        color: {t['button_text']};
        border: none;
        border-radius: 8px;
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background: {t['accent']};
        opacity: 0.9;
    }}
    QPushButton:pressed {{
        background: {t['accent']};
    }}
    QPushButton.secondary {{
        background: {t['hover']};
        color: {t['text']};
        border: 1px solid {t['border']};
    }}
    QPushButton.danger {{
        background: {t['priority_high']};
        color: white;
    }}
    
    QCheckBox {{
        spacing: 6px;
        color: {t['text']};
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid {t['border']};
        background: {t['input_bg']};
    }}
    QCheckBox::indicator:checked {{
        background: {t['accent']};
        border: 1px solid {t['accent']};
    }}
    
    QLabel {{
        color: {t['text']};
        background: transparent;
    }}
    QLabel.secondary {{
        color: {t['text_secondary']};
        font-size: {fs - 1}px;
    }}
    
    QMenu {{
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 6px 24px;
        border-radius: 6px;
        color: {t['text']};
    }}
    QMenu::item:selected {{
        background: {t['hover']};
    }}
    
    QDialog {{
        background: {t['window']};
        border-radius: 12px;
    }}
    
    QDateTimeEdit {{
    background: {t['input_bg']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 4px 8px;
    color: {t['text']};
}}

/* 日历弹出窗口样式 */
QCalendarWidget {{
    background: {t['window']};
    border: 1px solid {t['border']};
    border-radius: 12px;
}}

QCalendarWidget QTableView {{
    background: {t['window']};
    color: {t['text']};
    border: none;
    selection-background-color: {t['accent']};
    selection-color: white;
    gridline-color: {t['border']};
}}

QCalendarWidget QTableView::item:selected {{
    background: {t['accent']};
    color: white;
    border-radius: 6px;
}}

QCalendarWidget QHeaderView::section {{
    background: {t['card']};
    color: {t['text']};
    border: none;
    padding: 6px;
    font-weight: bold;
}}

QCalendarWidget QToolButton {{
    background: {t['card']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 4px;
}}

QCalendarWidget QToolButton:hover {{
    background: {t['hover']};
}}

QCalendarWidget QSpinBox {{
    background: {t['input_bg']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 4px;
}}
    
    QSpinBox {{
        background: {t['input_bg']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        padding: 4px 8px;
        color: {t['text']};
    }}
    """

def get_card_stylesheet(theme, priority_color, completed=False):
    t = theme
    opacity = "0.5" if completed else "1.0"
    border_color = priority_color if not completed else t['border']
    return f"""
    QWidget#TaskCard {{
        background: {t['card']};
        border: 1px solid {border_color};
        border-radius: 12px;
        opacity: {opacity};
    }}
    QWidget#TaskCard:hover {{
        background: {t['hover']};
        border: 1px solid {t['accent']};
    }}
    """

class StyleHelper:
    @staticmethod
    def apply_font(widget, family, size, bold=False):
        font = QFont(family, size)
        if bold:
            font.setBold(True)
        widget.setFont(font)
    
    @staticmethod
    def make_circle_button(color, size=20):
        from PyQt5.QtWidgets import QPushButton
        btn = QPushButton()
        btn.setFixedSize(size, size)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                border-radius: {size//2}px;
                border: none;
            }}
            QPushButton:hover {{
                border: 2px solid white;
            }}
        """)
        return btn
