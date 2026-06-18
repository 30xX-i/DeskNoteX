import sys
import os
from PyQt5.QtGui import QIcon

# Add src to path
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.ui.main_window import MainWindow
from src.core.platform_utils import setup_platform_app, get_app_icon_path


def _resolve_window_icon() -> QIcon:
    """解析主窗口图标,资源缺失时回退到 Qt 内置标准图标。"""
    icon_path = get_app_icon_path()
    if icon_path:
        icon = QIcon(icon_path)
        if not icon.isNull():
            return icon
    return QApplication.style().standardIcon(QApplication.style().SP_ComputerIcon)


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    setup_platform_app()

    app.setWindowIcon(_resolve_window_icon())

    window = MainWindow()
    window.show()

    from src.core.managers import TrayManager
    window.tray_manager = TrayManager(app, window, window.config)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()