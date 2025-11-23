from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QTimer, QEvent
from PyQt6.QtGui import QAction, QIcon
import psutil
from view import Ui_Form
import sys
import os
import ctypes

class App(QMainWindow):
    WARNING_THRESHOLD_RAM = 95
    WARNING_THRESHOLD_CPU = 80
    ICON_PATH = "app_icon.ico"
    TITLE = "System Dashboard"

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
    
    def __init__(self):
        super(App, self).__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        myappid = 'mycompany.system_dashboard.program.v1' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        icon_path = self.resource_path(self.ICON_PATH)

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            
            print(f"İkon bulunamadı: {icon_path}")

        self.cpu_percent = 0
        self.ram_percent = 0
        self.disk_percent = 0

        self.warning_show_cpu = False
        self.warning_show_ram = False


        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

        self.init_system_tray()

    def update_ui(self):
        self.cpu_percent = psutil.cpu_percent(interval=None)
        self.ram_percent = psutil.virtual_memory().percent
        self.disk_percent = psutil.disk_usage('C:\\').percent

        self.ui.pbCpuUsage.setValue(round(self.cpu_percent))
        self.ui.pbRamUsage.setValue(round(self.ram_percent))
        self.ui.pbDiscUsage.setValue(round(self.disk_percent))

        self.check_warnings()

    def check_warnings(self):
        if self.ui.cbWarner.isChecked():
            if self.cpu_percent >= self.WARNING_THRESHOLD_CPU and not self.warning_show_cpu:
                self.show_msg("UYARI!", "CPU kullanımı çok yüksek.", QMessageBox.Icon.Warning)
                
                self.warning_show_cpu = True 
            
            elif self.cpu_percent < self.WARNING_THRESHOLD_CPU:
                self.warning_show_cpu = False
            
            if self.ram_percent >= self.WARNING_THRESHOLD_RAM and not self.warning_show_ram:
                self.show_msg("UYARI!", "RAM kullanımı çok yüksek.", QMessageBox.Icon.Warning)
                
                self.warning_show_ram = True 
            
            elif self.ram_percent < self.WARNING_THRESHOLD_RAM:
                self.warning_show_ram = False
    
    def show_msg(self, title, message, icon: QMessageBox.Icon):
        msgBox = QMessageBox(self)
        msgBox.setIcon(icon)

        icon_path = self.resource_path(self.ICON_PATH)
        msgBox.setWindowIcon(QIcon(icon_path))

        msgBox.setText(message)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)

        return msgBox.exec()

    def init_system_tray(self):
        self.tray_icon = QSystemTrayIcon()
        tray_icon_path = self.resource_path(self.ICON_PATH)
        self.tray_icon.setIcon(QIcon(tray_icon_path))
        self.tray_icon.setToolTip(self.TITLE)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.menu = QMenu()
        self.show_action = QAction("Göster", self)
        self.show_action.triggered.connect(self.show)

        self.quit_app_action = QAction("Çıkış", self)
        self.quit_app_action.triggered.connect(self.quit_app)

        self.menu.addAction(self.show_action)
        self.menu.addAction(self.quit_app_action)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
    
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()


    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = App()
    window.show()
    sys.exit(app.exec())