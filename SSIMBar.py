from tkinter import W
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen
from cv2 import threshold

class SSIMBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.threshold = None

    def initUI(self, threshold):
        self.threshold = threshold

    def paintEvent(self, event):
        QProgressBar.paintEvent(self, event)
        if self.threshold:
            qp = QPainter(self)
            qb = QBrush(Qt.BrushStyle.SolidPattern)
            qb.setColor(QColor(0, 0, 0))
            qp.setPen(QPen(qb, 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            w = self.width()
            h = self.height()
            qp.drawLine(int(w * self.threshold / 100), 0, int(w * self.threshold / 100), h)

    @pyqtSlot(float)
    def displaySSIM(self, value):
        self.setValue(int(value))
        self.setFormat(f" SSIM: {value}%")
        if value >= self.threshold:
            self.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: green;
                }
            """)
        else:
            self.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: red;
                }
            """)