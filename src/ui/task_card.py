from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, 
    QPushButton, QMenu, QAction, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class TaskCard(QWidget):
    clicked = pyqtSignal(int)
    toggle_completed = pyqtSignal(int, bool)
    delete_task = pyqtSignal(int)
    edit_task = pyqtSignal(int)
    archive_task = pyqtSignal(int)
    restore_task = pyqtSignal(int)
    
    def __init__(self, task, theme, font_family, font_size, parent=None):
        super().__init__(parent)
        self.task_id = task['id']
        self.task = task
        self.theme = theme
        self.font_family = font_family
        self.font_size = font_size
        self._setup_ui()
    
    def _setup_ui(self):
        priority = self.task.get('priority', 1)
        priority_colors = {
            2: self.theme['priority_high'],
            1: self.theme['priority_mid'],
            0: self.theme['priority_low'],
        }
        priority_color = priority_colors.get(priority, self.theme['priority_mid'])
        completed = self.task.get('status', 0) == 1
        
        self.setObjectName("TaskCard")
        self.setStyleSheet(f"""
            QWidget#TaskCard {{
                background: {self.theme['card']};
                border: 1px solid {priority_color if not completed else self.theme['border']};
                border-radius: 12px;
            }}
            QWidget#TaskCard:hover {{
                background: {self.theme['hover']};
                border: 1px solid {self.theme['accent']};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        # Checkbox
        self.check = QCheckBox()
        self.check.setChecked(completed)
        self.check.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {priority_color};
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background: {priority_color};
                border: 2px solid {priority_color};
            }}
            QCheckBox::indicator:checked::after {{
                content: "";
            }}
        """)
        self.check.stateChanged.connect(self._on_check_changed)
        layout.addWidget(self.check, 0, Qt.AlignTop)
        
        # Content
        content = QVBoxLayout()
        content.setSpacing(4)
        
        title = self.task.get('title', '')
        self.title_label = QLabel(title)
        font = QFont(self.font_family, self.font_size)
        if completed:
            font.setStrikeOut(True)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(f"color: {self.theme['text']};")
        self.title_label.setWordWrap(True)
        content.addWidget(self.title_label)
        
        # Meta row
        meta = QHBoxLayout()
        meta.setSpacing(6)
        
        due = self.task.get('due_date')
        if due:
            due_lbl = QLabel(f"📅 {due[:10]}")
            due_lbl.setStyleSheet(f"color: {self.theme['text_secondary']}; font-size: {self.font_size - 1}px;")
            meta.addWidget(due_lbl)
        
        cat = self.task.get('category_name')
        if cat:
            cat_color = self.task.get('category_color', self.theme['accent'])
            cat_lbl = QLabel(f"● {cat}")
            cat_lbl.setStyleSheet(f"color: {cat_color}; font-size: {self.font_size - 1}px;")
            meta.addWidget(cat_lbl)
        
        pri_names = {2: "高", 1: "中", 0: "低"}
        pri_lbl = QLabel(f"{'🔴' if priority==2 else '🟡' if priority==1 else '🟢'} {pri_names.get(priority, '中')}")
        pri_lbl.setStyleSheet(f"color: {priority_color}; font-size: {self.font_size - 1}px;")
        meta.addWidget(pri_lbl)
        
        meta.addStretch()
        content.addLayout(meta)
        
        layout.addLayout(content, 1)
        
        # Menu button
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFixedSize(24, 24)
        self.menu_btn.setStyleSheet(f"""
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
        self.menu_btn.clicked.connect(self._show_menu)
        layout.addWidget(self.menu_btn, 0, Qt.AlignTop)
        
        self.setMaximumHeight(80)
        self.setMinimumHeight(60)
    
    def _on_check_changed(self, state):
        self.toggle_completed.emit(self.task_id, state == Qt.Checked)
    
    def _show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {self.theme['card']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 6px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 6px;
                color: {self.theme['text']};
            }}
            QMenu::item:selected {{
                background: {self.theme['hover']};
            }}
        """)
        
        edit_action = QAction("编辑", menu)
        edit_action.triggered.connect(lambda: self.edit_task.emit(self.task_id))
        menu.addAction(edit_action)
        
        if self.task.get('archived', 0) == 0:
            if self.task.get('status', 0) == 1:
                archive_action = QAction("归档", menu)
                archive_action.triggered.connect(lambda: self.archive_task.emit(self.task_id))
                menu.addAction(archive_action)
        else:
            restore_action = QAction("恢复", menu)
            restore_action.triggered.connect(lambda: self.restore_task.emit(self.task_id))
            menu.addAction(restore_action)
        
        delete_action = QAction("删除", menu)

        delete_action.triggered.connect(lambda: self.delete_task.emit(self.task_id))
        menu.addAction(delete_action)
        
        menu.exec_(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.check.geometry().contains(event.pos()):
            self.clicked.emit(self.task_id)
    
    def update_completed(self, completed):
        self.task['status'] = 1 if completed else 0
        font = self.title_label.font()
        font.setStrikeOut(completed)
        self.title_label.setFont(font)

class CategoryItem(QWidget):
    selected = pyqtSignal(int)
    
    def __init__(self, category, theme, font_family, font_size, active=False, parent=None):
        super().__init__(parent)
        self.cat_id = category['id']
        self.cat_name = category['name']
        self.color = category.get('color', theme['accent'])
        self.theme = theme
        self.font_family = font_family
        self.font_size = font_size
        self.active = active
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {self.color + '30' if self.active else 'transparent'};
                border-radius: 8px;
            }}
            QWidget:hover {{
                background: {self.theme['hover']};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)
        
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {self.color}; font-size: {self.font_size}px;")
        layout.addWidget(dot)
        
        lbl = QLabel(self.cat_name)
        lbl.setStyleSheet(f"color: {self.theme['text']}; font-size: {self.font_size}px;")
        layout.addWidget(lbl)
        layout.addStretch()
    
    def set_active(self, active):
        self.active = active
        self.setStyleSheet(f"""
            QWidget {{
                background: {self.color + '30' if self.active else 'transparent'};
                border-radius: 8px;
            }}
            QWidget:hover {{
                background: {self.theme['hover']};
            }}
        """)
    
    def mousePressEvent(self, event):
        self.selected.emit(self.cat_id)
