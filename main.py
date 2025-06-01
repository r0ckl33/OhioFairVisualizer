import sys
from PyQt6.QtWidgets import QApplication
from controllers.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    controller = MainController()
    controller.cal_win.closeEvent = lambda event: (app.quit(), event.accept())
    controller.show_all_windows()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
