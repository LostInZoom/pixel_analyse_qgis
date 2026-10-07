from qgis.PyQt.QtWidgets import (QDialog,QVBoxLayout,QLabel,QComboBox,QPushButton,QTextEdit)
from .models import SCREEN_MODELS
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsPointXY,QgsGeometry,QgsWkbTypes)
from qgis.PyQt.QtCore import Qt, QRect
from .analysis import analyze_pixels
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
        self.setWindowTitle("Pixel Energy")
        self.resize(400, 400)
        layout = QVBoxLayout()

        # Modèle
        layout.addWidget(QLabel("Modèle d'écran :"))

        self.model_combo = QComboBox()
        for model_id, model in SCREEN_MODELS.items():
            self.model_combo.addItem(model["name"],model_id)

        layout.addWidget(self.model_combo)

        # Sélection

        self.select_button = QPushButton("Sélectionner une zone")

        layout.addWidget(self.select_button)
        self.select_button.clicked.connect(self.start_selection)

        self.canvas_button = QPushButton("Analyser tout le canvas")

        layout.addWidget(self.canvas_button)

        self.canvas_button.clicked.connect(self.analyze_full_canvas)
        # Résultats

        layout.addWidget(QLabel("Résultats :"))
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


        text += "===== ZONE SÉLECTIONNÉE =====\n\n"

        text += "Emprise géographique\n"
        text += f"  xmin : {xmin:.2f}\n"
        text += f"  xmax : {xmax:.2f}\n"
        text += f"  ymin : {ymin:.2f}\n"
        text += f"  ymax : {ymax:.2f}\n\n"

        text += "Emprise écran\n"
        text += f"  x : {x}\n"
        text += f"  y : {y}\n"
        text += f"  largeur : {width} px\n"
        text += f"  hauteur : {height} px\n\n"


        text += "===== RÉSULTATS =====\n\n"

        text += f"Nombre de pixels : {result['pixelCount']}\n\n"

        text += "RGB\n"
        text += f"  Rouge   : {result['rgb']['red']['mean']:.2f} "
        text += f"(σ = {result['rgb']['red']['std']:.2f})\n"

        text += f"  Vert    : {result['rgb']['green']['mean']:.2f} "
        text += f"(σ = {result['rgb']['green']['std']:.2f})\n"

        text += f"  Bleu    : {result['rgb']['blue']['mean']:.2f} "
        text += f"(σ = {result['rgb']['blue']['std']:.2f})\n\n"

        text += "Luminance\n"
        text += f"  Moyenne : {result['luminance']['mean']:.2f}\n"
        text += f"  Écart-type : {result['luminance']['std']:.2f}\n\n"

        text += "Énergie\n"
        text += f"  Puissance écran : "
        text += f"{result['energy']['p_total_ecran']:.4f} W\n"

        text += f"  Puissance / pixel : "
        text += f"{result['energy']['p_pixel']:.6e} W\n"

        text += f"  Ratio moyen : "
        text += f"{result['energy']['mean_ratio']:.4f}\n\n"

        text += f"Modèle : {result['energy']['model']}\n"

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
        model = SCREEN_MODELS[model_id]
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
        model = SCREEN_MODELS[model_id]


        result = analyze_pixels(image,model)


        extent = canvas.extent()

        xmin = extent.xMinimum()
        xmax = extent.xMaximum()
        ymin = extent.yMinimum()
        ymax = extent.yMaximum()


        self.display_results(result,xmin,xmax,ymin,ymax,x,y,width,height) 
