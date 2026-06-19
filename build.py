import PyInstaller.__main__
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(here, "main.py")

# PyInstaller 的 --add-data 分隔符:
#   Windows 用 ';'
#   macOS / Linux 用 ':'
# 在 macOS 上写 ';' 会直接报 "Wrong syntax, should be --add-data=SOURCE:DEST"。
_add_data_sep = ";" if sys.platform.startswith("win") else ":"

args = [
    main_script,
    "--name=DeskNoteX",
    "--onefile",
    "--windowed",
    "--noconsole",
    # Exclude heavy Qt modules to reduce size
    "--exclude-module=PyQt5.QtWebEngine",
    "--exclude-module=PyQt5.QtWebEngineCore",
    "--exclude-module=PyQt5.QtWebEngineWidgets",
    "--exclude-module=PyQt5.QtWebKit",
    "--exclude-module=PyQt5.QtWebKitWidgets",
    "--exclude-module=PyQt5.Qt3D",
    "--exclude-module=PyQt5.Qt3DRender",
    "--exclude-module=PyQt5.Qt3DInput",
    "--exclude-module=PyQt5.Qt3DLogic",
    "--exclude-module=PyQt5.Qt3DExtras",
    "--exclude-module=PyQt5.QtMultimedia",
    "--exclude-module=PyQt5.QtMultimediaWidgets",
    "--exclude-module=PyQt5.QtBluetooth",
    "--exclude-module=PyQt5.QtLocation",
    "--exclude-module=PyQt5.QtPositioning",
    "--exclude-module=PyQt5.QtSensors",
    "--exclude-module=PyQt5.QtSerialPort",
    "--exclude-module=PyQt5.QtSql",
    "--exclude-module=PyQt5.QtTest",
    "--exclude-module=PyQt5.QtXml",
    "--exclude-module=PyQt5.QtXmlPatterns",
    "--exclude-module=PyQt5.QtNetwork",
    "--exclude-module=PyQt5.QtDesigner",
    "--exclude-module=PyQt5.QtHelp",
    "--exclude-module=PyQt5.QtOpenGL",
    "--exclude-module=PyQt5.QtPrintSupport",
    "--exclude-module=PyQt5.QtSvg",
    "--exclude-module=PyQt5.QtCharts",
    "--exclude-module=PyQt5.QtDataVisualization",
    "--exclude-module=PyQt5.QtQuick",
    "--exclude-module=PyQt5.QtQuickWidgets",
    "--exclude-module=PyQt5.QtQml",
    "--exclude-module=PyQt5.QtNfc",
    # Data(分隔符按平台区分,见 _add_data_sep 定义)
    f"--add-data=assets{_add_data_sep}assets",
    # Output
    "--distpath=dist",
    "--workpath=build",
    "--specpath=.",
    # Icon(macOS 优先用 .icns;若仓库只有 .ico,PyInstaller 也能用但显示效果差)
    ("--icon=assets/icon.icns" if sys.platform == "darwin"
     and os.path.exists(os.path.join(here, "assets", "icon.icns"))
     else "--icon=assets/icon.ico"),
]

PyInstaller.__main__.run(args)