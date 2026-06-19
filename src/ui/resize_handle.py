"""右下角 resize grip(透明,无视觉)。

仅作为鼠标事件捕获区域,按住拖动调整父窗口大小。
不画任何东西 —— 用户在 macOS 上看不到任何 grip 标记,
但 hover 进入区域时仍会自动切换为 SizeFDiagCursor,
按住拖动可 resize 窗口(与 minimumSize / maximumSize 兼容)。

不依赖 QSizeGrip,避免后者在某些 Qt 版本下影响父 widget 的样式继承。
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget


GRIP_SIZE = 16


class ResizeHandle(QWidget):
    """右下角不可见 grip,按住拖动调整父窗口大小。

    父窗口会被 resize 到鼠标拖动距离 + 起始 size,
    且不超过父窗口的 minimumSize / maximumSize。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(GRIP_SIZE, GRIP_SIZE)
        self.setMouseTracking(True)
        self._dragging = False
        self._drag_start_pos = None
        self._drag_start_size = None

    def enterEvent(self, event):
        # 进入区域:切换光标为 macOS 原生 resize 斜箭头
        self.setCursor(Qt.SizeFDiagCursor)

    def leaveEvent(self, event):
        if not self._dragging:
            self.unsetCursor()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPos()
            self._drag_start_size = self.parent().size()

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_start_pos is not None:
            parent = self.parent()
            delta = event.globalPos() - self._drag_start_pos
            new_w = max(
                parent.minimumWidth(),
                self._drag_start_size.width() + delta.x(),
            )
            new_h = max(
                parent.minimumHeight(),
                self._drag_start_size.height() + delta.y(),
            )
            max_size = parent.maximumSize()
            if max_size.width() < 16777215:  # QWIDGETSIZE_MAX
                new_w = min(new_w, max_size.width())
            if max_size.height() < 16777215:
                new_h = min(new_h, max_size.height())
            parent.resize(new_w, new_h)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
