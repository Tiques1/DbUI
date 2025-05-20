from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import pyodbc
import os


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Hello World")

        layout = QGridLayout()
        self.setLayout(layout)

        label = QLabel("Hello World!")
        layout.addWidget(label, 0, 0)

        # The BoxLayout is similar to the GridLayout, however it only supports a single row or column of widgets depending
        # on the orientation. It does however dynamically size to the number of widgets it is to contain.
        
        # Direction { LeftToRight, RightToLeft, TopToBottom, BottomToTop } или Horizontal или Vertical
        boxlayout = QBoxLayout(QBoxLayout.LeftToRight)

        # boxlayout.addWidget(widget, stretch, alignment)
        # boxlayout.insertWidget(index, widget, stretch, alignment)
        # Qt.AlignmentLeft
        # Qt.AlignmentRight
        # Qt.AlignmentHCenter
        # Qt.AlignmentJustify

        # boxlayout.addLayout(layout, stretch)
        # boxlayout.insertLayout(index, layout, stretch)

        # boxlayout.setSpacing(spacing)
        # boxlayout.addSpacing(spacing)
        # boxlayout.insertSpacing(index, spacing)



        self.resize(400, 300)

app = QApplication(sys.argv)
screen = Window()

screen.show()
label = QLabel("Hello world2")
sys.exit(app.exec_())

# window.showMinimized()
# window.showMaximized()
# window.showFullScreen()
# window.setNormal()
# window.setMinimumWidth(width)
# window.setMaximumWidth(width)
# window.setMinimumHeight(height)
# window.setMaximumHeight(height)
