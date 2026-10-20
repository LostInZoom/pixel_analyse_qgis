import os

from qgis.PyQt.QtCore import QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import QAction

from .dialog import PixelEnergyDialog



class PixelEnergy:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None
        self.translator = None
        

        locale = QCoreApplication.instance().property("locale/userLocale")

        if not locale:
            locale = "en"

        language = locale[:2].lower()

        if language not in ("fr", "en"):
            language = "en"

        if language != "en":
            plugin_dir = os.path.dirname(__file__)
            translation_file = os.path.join(
                plugin_dir,
                "i18n",
                f"pixel_analyse_qgis_{language}.qm"
            )

            if os.path.exists(translation_file):
                self.translator = QTranslator()
                if self.translator.load(translation_file):
                    QCoreApplication.installTranslator(self.translator)
                else:
                    self.translator = None


    def initGui(self):
        self.action = QAction("Pixel Energy",self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&Pixel Energy",self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginMenu("&Pixel Energy",self.action)
            self.iface.removeToolBarIcon(self.action)
            if self.translator:
                QCoreApplication.removeTranslator(self.translator)
                self.translator = None

    def run(self):

        if self.dialog is None:
            self.dialog = PixelEnergyDialog(self.iface)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()