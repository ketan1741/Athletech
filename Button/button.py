from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
import subprocess
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(400, 300)

        # Create a button
        button_logger = QPushButton("Start Logger", self)
        button_logger.setGeometry(130, 10, 150, 70)

        # Connect button clicked signal to a slot
        button_logger.clicked.connect(self.start_logger)

        # Create a button
        button_ocr = QPushButton("Start OCR", self)
        button_ocr.setGeometry(130, 90, 150, 70)

        # Connect button clicked signal to a slot
        button_ocr.clicked.connect(self.start_ocr)

        # Create a button
        button_stream = QPushButton("Start Stream", self)
        button_stream.setGeometry(130, 170, 150, 70)

        # Connect button clicked signal to a slot
        button_stream.clicked.connect(self.start_stream)

    def start_logger(self):
        # Code to execute when the button is clicked
        subprocess.Popen([sys.executable, "loggerScript.py"])

    def start_ocr(self):
        subprocess.Popen([sys.executable, "ocr_main.py"])

    def start_stream(self):
        subprocess.Popen([sys.executable, "stream_obs.py"])

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
