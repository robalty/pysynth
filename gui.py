import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout
from PyQt5.QtGui import QIcon, QPixmap

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PySynth - Feel the wave'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        layout = QGridLayout()

        # Create the splash image widget
        label = QLabel(self)
        pixmap = QPixmap('synthwave.jpg')
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())


        # Set up the widget grid layout
        layout.addWidget(label, 0, 0)
        self.setLayout(layout)
        
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
