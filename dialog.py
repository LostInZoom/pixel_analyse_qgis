from unittest import result

from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)
from qgis.PyQt.QtCore import Qt, QRect
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsPointXY, QgsGeometry, QgsWkbTypes

from .models import SCREEN_MODELS
from .analysis import analyze_pixels
from .model_editor import ModelEditorDialog
from .model_storage import load_custom_models, delete_custom_model



class RectangleMapTool(QgsMapTool):

    def __init__(self, canvas, callback):
        super().__init__(canvas)

        self.canvas = canvas
        self.callback = callback
        self.start_point = None
        self.end_point = None

        self.rubber_band = QgsRubberBand(canvas,QgsWkbTypes.PolygonGeometry)

        self.rubber_band.setColor(QColor(255, 0, 0, 100))
        self.rubber_band.setWidth(2)

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_screen = event.pos()
            self.start_point = self.toMapCoordinates(event.pos())
            self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)

    def canvasMoveEvent(self, event):
        if self.start_point is None:
            return
        self.end_point = self.toMapCoordinates(event.pos())
        self.update_rectangle()

    def canvasReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        if self.start_point is None:
            return
        self.end_point = self.toMapCoordinates(event.pos())
        self.end_screen = event.pos()
        end_screen = self.end_screen    
        self.update_rectangle()

        start = self.start_point
        start_screen = self.start_screen
        end = self.end_point
        
        self.start_point = None
        self.end_point = None
        
        self.callback(start, end,start_screen,end_screen)
        
    def update_rectangle(self):

        x1 = self.start_point.x()
        y1 = self.start_point.y()

        x2 = self.end_point.x()
        y2 = self.end_point.y()

        points = [
            QgsPointXY(x1, y1),
            QgsPointXY(x2, y1),
            QgsPointXY(x2, y2),
            QgsPointXY(x1, y2),
            QgsPointXY(x1, y1)
        ]

        self.rubber_band.setToGeometry(QgsGeometry.fromPolygonXY([points]),None)

    def clear_selection(self):
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
class PixelEnergyDialog(QDialog):

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle(self.tr("Pixel Energy"))
        self.resize(400, 400)
        layout = QVBoxLayout()

        # Modèle
        layout.addWidget(QLabel(self.tr("Screen model:")))

        # self.model_combo = QComboBox()
        # for model_id, model in SCREEN_MODELS.items():
        #     self.model_combo.addItem(model["name"],model_id)

        # layout.addWidget(self.model_combo)
        
        self.model_combo = QComboBox()

        self.refresh_models()

        model_layout = QHBoxLayout()
        model_layout.addWidget(self.model_combo)

        self.manage_models_button = QPushButton(
            self.tr("• Manage models…")
        )
        model_layout.addWidget(self.manage_models_button)

        layout.addLayout(model_layout)

        self.manage_models_button.clicked.connect(self.manage_models)

        # Sélection

        self.select_button = QPushButton(self.tr("Select a area"))

        layout.addWidget(self.select_button)
        self.select_button.clicked.connect(self.start_selection)

        self.canvas_button = QPushButton(self.tr("Analyze entire canvas"))

        layout.addWidget(self.canvas_button)

        self.canvas_button.clicked.connect(self.analyze_full_canvas)
        # Résultats

        layout.addWidget(QLabel(self.tr("Results :")))
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        
        layout.addWidget(self.results)
        self.setLayout(layout)

    def start_selection(self):
        canvas = self.iface.mapCanvas()
        self.previous_map_tool = canvas.mapTool()

        if hasattr(self, "map_tool") and self.map_tool is not None:
            self.map_tool.clear_selection()


        self.map_tool = RectangleMapTool(canvas,self.rectangle_selected)

        canvas.setMapTool(self.map_tool)

    def point_clicked(self, point, button):

        print("Point sélectionné :", point)
        canvas = self.iface.mapCanvas()
        print("Coordonnées géographiques :",point.x(),point.y())
        print("Taille du canvas :",canvas.width(),"x",canvas.height())

    def display_results(self, result, xmin, xmax, ymin, ymax, x, y, width, height):

        text = ""


        text += self.tr("===== SELECTED AREA =====\n\n")

        text += self.tr("Geographic extent\n")
        text += f"  xmin : {xmin:.2f}\n"
        text += f"  xmax : {xmax:.2f}\n"
        text += f"  ymin : {ymin:.2f}\n"
        text += f"  ymax : {ymax:.2f}\n\n"

        text += self.tr("Screen extent\n")
        text += f"  x : {x}\n"
        text += f"  y : {y}\n"
        text += f"  {self.tr('width')} : {width} px\n"
        text += f"  {self.tr('height')} : {height} px\n\n"


        text += self.tr("===== RESULTS =====\n\n")

        text += f"{self.tr('Number of pixels')} : "
        text += f"{result['pixelCount']}\n\n"

        text += self.tr("RGB\n")
        text += f"  {self.tr('Red')} :  {result['rgb']['red']['mean']:.2f} "
        text += f"(σ = {result['rgb']['red']['std']:.2f})\n"

        text += f"  {self.tr('Green')}    : {result['rgb']['green']['mean']:.2f} "
        text += f"(σ = {result['rgb']['green']['std']:.2f})\n"

        text += f"  {self.tr('Blue')}    : {result['rgb']['blue']['mean']:.2f} "
        text += f"(σ = {result['rgb']['blue']['std']:.2f})\n\n"

        text += self.tr("Luminance\n")
        text += f"  {self.tr('Mean')} : {result['luminance']['mean']:.2f}\n"
        text += f"  {self.tr('Standard deviation')} : {result['luminance']['std']:.2f}\n\n"
        if result["energy"]["type"] == "power":
            text += self.tr("Energy\n")
            text += f"  {self.tr('Screen power')} : "
            text += f"{result['energy']['p_total_ecran']:.4f} W\n"

            text += f"  {self.tr('Power / pixel')} : "
            text += f"{result['energy']['p_pixel']:.6e}"
            text += f" {result['energy']['unit']}\n"

            text += f"  {self.tr('Model')} : {result['energy']['model']}\n"
        if result["energy"]["type"] == "indicator":
            text += self.tr("Indicator\n")
            text += f"  {self.tr('Indicator')} : "
            text += f"{result['energy']['indicator']:.4f}\n"

            text += f"  {self.tr('Model')} : {result['energy']['model']}\n"
            text += f"  {self.tr('Min')} : {result['energy']['min']}\n"
            text += f"  {self.tr('Max')} : {result['energy']['max']}\n"

        self.results.setPlainText(text)


    def rectangle_selected(self, start_point, end_point,start_screen,end_screen):


        xmin = min(start_point.x(), end_point.x())
        xmax = max(start_point.x(), end_point.x())
        ymin = min(start_point.y(), end_point.y())
        ymax = max(start_point.y(), end_point.y())
        x = min(start_screen.x(), end_screen.x())
        y = min(start_screen.y(), end_screen.y())
        width = abs(end_screen.x() - start_screen.x())
        height = abs(end_screen.y() - start_screen.y())


        canvas = self.iface.mapCanvas()

        rect = QRect(x,y,width,height)
        pixmap = canvas.grab(rect)
        image = pixmap.toImage()
        model_id = self.model_combo.currentData()
        model = self.models[model_id]
        result = analyze_pixels(image, model)
        self.display_results(result,xmin,xmax,ymin,ymax,x,y,width,height) 

        self.map_tool.clear_selection()
        canvas = self.iface.mapCanvas()

        if hasattr(self, "previous_map_tool") and self.previous_map_tool is not None:
            canvas.setMapTool(self.previous_map_tool)
        # self.iface.mapCanvas().unsetMapTool(self.map_tool)

    def analyze_full_canvas(self):
    
        canvas = self.iface.mapCanvas()

        width = canvas.width()
        height = canvas.height()
        x = 0
        y = 0
        rect = QRect(x,y,width,height)

        pixmap = canvas.grab(rect)
        image = pixmap.toImage()

        model_id = self.model_combo.currentData()
        model = self.models[model_id]


        result = analyze_pixels(image,model)


        extent = canvas.extent()

        xmin = extent.xMinimum()
        xmax = extent.xMaximum()
        ymin = extent.yMinimum()
        ymax = extent.yMaximum()


        self.display_results(result,xmin,xmax,ymin,ymax,x,y,width,height) 

    def refresh_models(self, selected_id=None):
        previous_id = (
            selected_id
            if selected_id is not None
            else self.model_combo.currentData()
            if hasattr(self, "model_combo")
            else None
        )

        models = dict(SCREEN_MODELS)

        for model in load_custom_models():
            models[model["id"]] = model

        self.models = models
        self.model_combo.clear()

        for model_id, model in models.items():
            self.model_combo.addItem(model["name"], model_id)

        index = self.model_combo.findData(previous_id)

        if index >= 0:
            self.model_combo.setCurrentIndex(index)


    def manage_models(self):
        selected_id = self.model_combo.currentData()

        dialog = ModelManagerDialog(self)
        dialog.exec_()

        self.refresh_models(selected_id)   

class ModelManagerDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Model management"))
        self.resize(420, 350)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(self.tr("Available models :")))

        self.model_list = QListWidget()
        layout.addWidget(self.model_list)

        buttons = QHBoxLayout()

        self.create_button = QPushButton(self.tr("Create"))
        self.edit_button = QPushButton(self.tr("Edit"))
        self.delete_button = QPushButton(self.tr("Delete"))

        buttons.addWidget(self.create_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)

        layout.addLayout(buttons)

        self.close_button = QPushButton(self.tr("Close"))
        layout.addWidget(self.close_button)

        self.create_button.clicked.connect(self.create_model)
        self.edit_button.clicked.connect(self.edit_model)
        self.delete_button.clicked.connect(self.delete_model)
        self.close_button.clicked.connect(self.accept)

        self.model_list.currentItemChanged.connect(self.update_buttons)
        self.model_list.itemDoubleClicked.connect(self.edit_model)

        self.refresh_list()

    def get_models(self):
        models = dict(SCREEN_MODELS)

        for model in load_custom_models():
            models[model["id"]] = model

        return models

    def refresh_list(self, selected_id=None):
        self.model_list.clear()
        models = self.get_models()

        for model_id, model in models.items():
            if model.get("built_in", True):
                label = f"{model['name']} (built-in)"
            else:
                label = f"{model['name']} (custom)"

            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, model_id)
            self.model_list.addItem(item)

            if model_id == selected_id:
                self.model_list.setCurrentItem(item)

        if self.model_list.currentItem() is None and self.model_list.count():
            self.model_list.setCurrentRow(0)

        self.update_buttons()

    def update_buttons(self, *args):
        item = self.model_list.currentItem()

        if item is None:
            is_custom = False
        else:
            model_id = item.data(Qt.UserRole)
            model = self.get_models().get(model_id, {})
            is_custom = not model.get("built_in", True)

        self.edit_button.setEnabled(is_custom)
        self.delete_button.setEnabled(is_custom)

    def create_model(self):
        editor = ModelEditorDialog(parent=self)

        if editor.exec_() == QDialog.Accepted:
            self.refresh_list(editor.model["id"])

    def edit_model(self, *args):
        item = self.model_list.currentItem()

        if item is None:
            return

        model_id = item.data(Qt.UserRole)
        model = self.get_models().get(model_id)

        if model is None or model.get("built_in", True):
            return

        editor = ModelEditorDialog(parent=self, model=model)

        if editor.exec_() == QDialog.Accepted:
            self.refresh_list(model_id)

    def delete_model(self):
        item = self.model_list.currentItem()

        if item is None:
            return

        model_id = item.data(Qt.UserRole)
        model = self.get_models().get(model_id)

        if model is None or model.get("built_in", True):
            return

        answer = QMessageBox.question(
            self,
            self.tr("Delete model"),
            self.tr("Delete model « {} » ?").format(model["name"]),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        try:
            delete_custom_model(model_id)
        except (ValueError, OSError) as error:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                str(error),
            )
            return

        self.refresh_list()

