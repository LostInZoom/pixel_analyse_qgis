from qgis.PyQt.QtWidgets import QAction

from .dialog import PixelEnergyDialog


class PixelEnergy:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        self.action = QAction("Pixel Energy",self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&Pixel Energy",self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginMenu("&Pixel Energy",self.action)
            self.iface.removeToolBarIcon(self.action)

    def run(self):

        if self.dialog is None:
            self.dialog = PixelEnergyDialog(self.iface)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()