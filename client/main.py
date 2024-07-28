import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QTextEdit,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt5.QtGui import QCursor
from loguru import logger

from core.pid import find_process_by_name, reconn_process_network_by_proc


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the window title and geometry
        self.setWindowTitle("hearth-stone-auto-reconnect-gui")
        self.setGeometry(500, 500, 800, 300)

        # Main layout
        layout = QVBoxLayout()

        # Log area
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # Button to open dialog
        self.button = QPushButton("Open Tool", self)
        self.button.clicked.connect(self.showDialog)
        layout.addWidget(self.button)

        # Copyright and GitHub link
        copyright_label = QLabel("V1.0 © 2024 ChenE2000")
        github_label = QLabel(
            '<a href="https://github.com/ChenE2000/hearth-stone-auto-reconnect-gui">GitHub</a>'
        )
        github_label.setOpenExternalLinks(True)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(copyright_label)
        bottom_layout.addWidget(github_label)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        # Set up loguru to redirect to the QTextEdit
        logger.remove()
        logger.add(QTextEditLogger(self.log_area))

        self.show()

    def showDialog(self):
        logger.debug("Dialog is being shown")
        self.dialog = DraggableDialog()
        self.dialog.show()


class DraggableDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window flags and attributes for a frameless, translucent dialog
        self.setWindowFlags(
            Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 200);")

        self.setGeometry(20, 20, 200, 150)

        # Main layout
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Reconnect button
        reconn_button = QPushButton("reconn", self)
        reconn_button.clicked.connect(self.reconn)
        button_layout.addWidget(reconn_button)

        # Indicator
        self.indicator = QLabel(self)
        self.indicator.setFixedSize(20, 20)
        button_layout.addWidget(self.indicator)

        # Close button styled as a circular button
        close_button = QPushButton("X", self)
        close_button.setStyleSheet(
            """
            QPushButton {
                color: white;
                background-color: red;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                min-width: 20px;
                min-height: 20px;
                max-width: 20px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """
        )
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close_dialog)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.old_pos = self.pos()
        self.is_reconnecting = False
        self.update_indicator()
        logger.debug("DraggableDialog initialized")

    def mousePressEvent(self, event):
        # Handle mouse press event for dragging the dialog
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event):
        # Handle mouse move event for dragging the dialog
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            event.accept()

    def mouseReleaseEvent(self, event):
        # Handle mouse release event
        self.setCursor(Qt.ArrowCursor)
        event.accept()
        logger.debug("Mouse released")

    def reconn(self):
        # Reconnect button functionality
        if self.is_reconnecting:
            logger.debug("Already reconnecting")
            return
        self.is_reconnecting = True
        self.update_indicator()
        self.thread = ReconnThread()
        self.thread.finished.connect(self.on_reconn_finished)
        self.thread.error_occurred.connect(self.on_error_occurred)
        self.thread.start()
        logger.debug("Reconnecting")

    def update_indicator(self):
        # Update the indicator color based on the reconnection status
        if self.is_reconnecting:
            self.indicator.setStyleSheet("background-color: red; border-radius: 10px;")
        else:
            self.indicator.setStyleSheet(
                "background-color: green; border-radius: 10px;"
            )

    def on_reconn_finished(self):
        # Handle reconnection completion
        self.is_reconnecting = False
        self.update_indicator()
        logger.debug("Reconnection finished")

    def on_error_occurred(self, error_message):
        # Handle reconnection error
        self.is_reconnecting = False
        self.update_indicator()
        logger.debug(f"Reconnection error: {error_message}")
        self.show_error_message(error_message)

    def close_dialog(self):
        # Close the dialog
        self.close()
        logger.debug("Dialog closed")

    def show_error_message(self, message):
        # Show an error message dialog
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


class ReconnThread(QThread):
    # Thread class for handling reconnection in the background
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            proc = find_process_by_name()
            reconn_process_network_by_proc(proc=proc)
            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))


class QTextEditLogger:
    # Custom logger to redirect log messages to a QTextEdit
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        if message.strip():
            self.text_edit.append(message.strip())

    def flush(self):
        pass


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
