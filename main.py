# main.py
# This is the main entry point of the application

import sys
from PyQt5.QtWidgets import QApplication
from main_gui import SurfaceIrrigationSystemDesign

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SurfaceIrrigationSystemDesign()
    window.show()
    sys.exit(app.exec_())
