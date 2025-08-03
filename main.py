import sys
from PyQt5 import QtWidgets, uic
from app.logic import ProdukLogic

class MainWindow(QtWidgets.QWidget):  # ✅ Ganti nama class!
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/form_produk.ui", self)
        self.logic = ProdukLogic(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
