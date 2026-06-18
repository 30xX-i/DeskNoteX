from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QSpinBox, QCheckBox, QWidget,
    QColorDialog, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .styles import get_stylesheet, StyleHelper


class SettingsDialog(QDialog):
    def __init__(self, parent, config, theme, font_family, font_size):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.config = config
        self.theme = theme
        self.font_family = font_family
        self.font_size = font_size
        self.result_config = None
        self._setup_ui()
    
    def _setup_ui(self):

        self.setStyleSheet(get_stylesheet(self.theme, self.font_family, self.font_size))
        
        container = QWidget(self)
        container.setObjectName("dialogContainer")
        container.setStyleSheet(f"""
            QWidget#dialogContainer {{
                background: {self.theme['window']};
                border-radius: 12px;
                border: 1px solid {self.theme['border']};
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        
        # Header
        header = QHBoxLayout()
        title_label = QLabel("设置")
        StyleHelper.apply_font(title_label, self.font_family, self.font_size + 2, True)
        header.addWidget(title_label)
        header.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.theme['text_secondary']};
                border-radius: 12px;
                font-size: {self.font_size}px;
            }}
            QPushButton:hover {{
                background: {self.theme['hover']};
                color: {self.theme['text']};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)
        
        # Theme
        layout.addWidget(QLabel("外观主题"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色模式", "light")
        self.theme_combo.addItem("深色模式", "dark")
        current = self.config.get("theme", "light")
        self.theme_combo.setCurrentIndex(0 if current == "light" else 1)
        layout.addWidget(self.theme_combo)
        
        # Always on top
        self.top_check = QCheckBox("窗口始终置顶")
        self.top_check.setChecked(self.config.get("always_on_top", True))
        layout.addWidget(self.top_check)
        
        # Auto tuck
        self.tuck_check = QCheckBox("边缘自动贴边收纳")
        self.tuck_check.setChecked(self.config.get("auto_tuck", True))
        layout.addWidget(self.tuck_check)
        
        # Notifications
        self.notify_check = QCheckBox("启用系统通知")
        self.notify_check.setChecked(self.config.get("notifications_enabled", True))
        layout.addWidget(self.notify_check)
        
        # Font
        layout.addWidget(QLabel("字体大小"))
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 16)
        self.font_spin.setValue(self.config.get("font_size", 10))
        layout.addWidget(self.font_spin)
        
        # Colors
        layout.addWidget(QLabel("自定义主题色"))
        color_grid = QGridLayout()
        color_grid = QGridLayout()
        color_grid.setSpacing(8)
        color_grid.setColumnStretch(0, 1)  # 标签列拉伸
        color_grid.setColumnStretch(1, 0)  # 按钮列固定

        self.color_inputs = {}
        color_keys = [
            ("accent", "强调色"),
            ("priority_high", "高优先级"),
            ("priority_mid", "中优先级"),
            ("priority_low", "低优先级"),
        ]

        custom_colors = self.config.get("custom_colors", {})
        for i, (key, label) in enumerate(color_keys):
            lbl = QLabel(label)
            lbl.setMinimumWidth(80)  # 设置标签最小宽度
            color_grid.addWidget(lbl, i, 0)

            btn = QPushButton()
            btn.setFixedSize(28, 28)
            color = custom_colors.get(key, self.theme.get(key))
            btn.setStyleSheet(f"background: {color}; border-radius: 14px; border: 1px solid {self.theme['border']};")
            btn.clicked.connect(lambda checked, k=key, b=btn: self._pick_color(k, b))
            color_grid.addWidget(btn, i, 1, alignment=Qt.AlignRight)  # 按钮右对齐
            self.color_inputs[key] = (btn, color)
        
        layout.addLayout(color_grid)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        self.setFixedSize(380, 450)
        self._center_on_parent()
    
    def _pick_color(self, key, btn):
        color = QColorDialog.getColor(QColor(self.color_inputs[key][1]), self, "选择颜色")
        if color.isValid():
            hex_color = color.name()
            self.color_inputs[key] = (btn, hex_color)
            btn.setStyleSheet(f"background: {hex_color}; border-radius: 14px; border: 1px solid {self.theme['border']};")
    
    def _center_on_parent(self):
        if self.parent():
            geo = self.geometry()
            parent_geo = self.parent().geometry()
            geo.moveCenter(parent_geo.center())
            self.setGeometry(geo)
    
    def _save(self):
        custom_colors = {}
        for key, (btn, color) in self.color_inputs.items():
            custom_colors[key] = color
        
        self.result_config = {
            "theme": self.theme_combo.currentData(),
            "always_on_top": self.top_check.isChecked(),
            "auto_tuck": self.tuck_check.isChecked(),
            "notifications_enabled": self.notify_check.isChecked(),
            "font_size": self.font_spin.value(),
            "custom_colors": custom_colors,
        }
        self.accept()
    
    def get_config(self):
        return self.result_config

class StatsDialog(QDialog):
    def __init__(self, parent, stats, theme, font_family, font_size, db):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.stats = stats
        self.theme = theme
        self.font_family = font_family
        self.font_size = font_size
        self.db = db
        self._setup_ui()
    
    def _setup_ui(self):

        self.setStyleSheet(get_stylesheet(self.theme, self.font_family, self.font_size))
        
        container = QWidget(self)
        container.setObjectName("dialogContainer")
        container.setStyleSheet(f"""
            QWidget#dialogContainer {{
                background: {self.theme['window']};
                border-radius: 12px;
                border: 1px solid {self.theme['border']};
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        header = QHBoxLayout()
        title_label = QLabel("数据统计")
        StyleHelper.apply_font(title_label, self.font_family, self.font_size + 2, True)
        header.addWidget(title_label)
        header.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.theme['text_secondary']};
                border-radius: 12px;
                font-size: {self.font_size}px;
            }}
            QPushButton:hover {{
                background: {self.theme['hover']};
                color: {self.theme['text']};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)
        
        total = self.stats.get("total", 0)
        completed = self.stats.get("completed", 0)
        rate = self.stats.get("completion_rate", 0)
        
        layout.addWidget(self._make_stat_label("任务总数", str(total)))
        layout.addWidget(self._make_stat_label("已完成", str(completed)))
        layout.addWidget(self._make_stat_label("完成率", f"{rate}%"))
        
        layout.addWidget(QLabel("分类分布"))
        by_cat = self.stats.get("by_category", {})
        categories = self.db.get_categories()
        for cat in categories:
            cnt = by_cat.get(cat['id'], 0)
            layout.addWidget(self._make_stat_label(f"  {cat['name']}", str(cnt)))
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("关闭")
        ok_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        self.setFixedSize(280, 300)
        self._center_on_parent()
    
    def _make_stat_label(self, label, value):
        h = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {self.theme['text_secondary']};")
        h.addWidget(lbl)
        h.addStretch()
        val = QLabel(value)
        StyleHelper.apply_font(val, self.font_family, self.font_size + 2, True)
        val.setStyleSheet(f"color: {self.theme['accent']};")
        h.addWidget(val)
        w = QWidget()
        w.setLayout(h)
        return w
    
    def _center_on_parent(self):
        if self.parent():
            geo = self.geometry()
            parent_geo = self.parent().geometry()
            geo.moveCenter(parent_geo.center())
            self.setGeometry(geo)
