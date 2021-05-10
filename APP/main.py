import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from qt_app import wormchan_app


def main():
    app = QtWidgets.QApplication(sys.argv)
    wormchan = wormchan_app()
    wormchan.show()
    sys.exit(app.exec_())


main()
