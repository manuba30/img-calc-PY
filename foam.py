import cv2
import numpy as np
import pyqtgraph as pg
from PySide6 import QtWidgets
from pydantic import BaseModel


# Modèle Pydantic pour la configuration
class AnalysisConfig(BaseModel):
    threshold_value: int = 127
    min_contour_area: float = 100.0


# Application PyQt avec PySide6
class ImageAnalyzerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Foam Structure Analyzer')
        self.setGeometry(100, 100, 1000, 800)

        # Créer une widget centrale
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Disposer les widgets
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Créer une widget graphique pour afficher l'image
        self.view = pg.GraphicsView()
        layout.addWidget(self.view)

        self.image_item = pg.ImageItem()

        # Créer un PlotItem pour ajouter l'image
        self.plot_item = pg.PlotItem()
        self.plot_item.addItem(self.image_item)
        self.view.setCentralItem(self.plot_item)

        # Ajouter des boutons
        self.load_button = QtWidgets.QPushButton('Load Image')
        self.load_button.clicked.connect(self.load_image)
        layout.addWidget(self.load_button)

        self.calculate_button = QtWidgets.QPushButton('Calculate Distances')
        self.calculate_button.clicked.connect(self.calculate_distances)
        layout.addWidget(self.calculate_button)

        self.status_label = QtWidgets.QLabel('Status: Ready')
        layout.addWidget(self.status_label)

        self.image = None
        self.config = AnalysisConfig()
        self.points = []  # Liste pour stocker les points sélectionnés

        # Charger l'image initiale
        self.load_image('1.jpg')

        # Connexion des événements de la souris--corrections a faire
        self.view.mouseClickEvent = self.mouse_click_event

    def load_image(self, file_name=None):
        if file_name is None:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Image File')
        if file_name:
            self.image = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
            self.display_image(self.image)
            self.status_label.setText('Status: Image Loaded')

    def display_image(self, image):
        # Convertir l'image de OpenCV à PyQtGraph
        if image is not None:
            self.image_item.setImage(image)
            self.plot_item.autoRange()  # Ajuster automatiquement la vue pour l'image

    def calculate_distances(self):
        if len(self.points) < 2:
            self.status_label.setText('Status: At least two points required')
            return

        distances = []
        for i in range(len(self.points)):
            for j in range(i + 1, len(self.points)):
                pt1 = np.array(self.points[i])
                pt2 = np.array(self.points[j])
                distance = np.linalg.norm(pt1 - pt2)
                distances.append(distance)

        self.status_label.setText(f'Status: Distances Calculated: {distances}')

        # Afficher les points sur l'image-- a corrigir
        self.plot_item.clear()
        self.plot_item.addItem(self.image_item)
        scatter = pg.ScatterPlotItem(x=[p[0] for p in self.points], y=[p[1] for p in self.points], symbol='o', pen='w',
                                     brush='r')
        self.plot_item.addItem(scatter)
        self.plot_item.autoRange()

    def mouse_click_event(self, event):
        pos = event.pos()
        if self.image is not None:
            # Convertir les coordonnées du clic en coordonnées de l'image
            img_pos = self.view.mapToScene(pos)
            self.points.append((img_pos.x(), img_pos.y()))
            self.status_label.setText(f'Status: Point added at {img_pos.x()}, {img_pos.y()}')
            # Afficher les points sur l'image
            scatter = pg.ScatterPlotItem(x=[p[0] for p in self.points], y=[p[1] for p in self.points], symbol='o',
                                         pen='w', brush='r')
            self.plot_item.addItem(scatter)

# Fonction principale
def main():
    app = QtWidgets.QApplication([])
    window = ImageAnalyzerApp()
    window.show()
    app.exec()

