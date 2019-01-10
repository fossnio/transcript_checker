import sys
import pathlib
from queue import Queue

from PySide2.QtWidgets import (QApplication, QWidget,
                               QPushButton, QTextEdit,
                               QVBoxLayout, QFileDialog,
                               QFormLayout, QLabel, QLineEdit,
                               QProgressBar)
from PySide2.QtCore import Slot, QThread
from check_transcript import check_transcript


class TranscriptWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('成績單檢查程式')
        self.resize(640, 480)

        self.transcript_text = QTextEdit()
        self.check_btn = QPushButton('選取成績單檔案')
        self.check_btn.clicked.connect(self.load_transcript_file)

        self.form_widget = QWidget()
        self.form_layout = QFormLayout()
        self.lable1 = QLabel("學生應出席日數")
        self.lineedit1 = QLineEdit()
        self.lineedit1.setToolTip('會用來比對每班學生是否實際出席日數都一樣，理論上不可能全班都沒人請假')
        self.lineedit1.setText('100')
        self.lable2 = QLabel("學生正常分數下限")
        self.lineedit2 = QLineEdit()
        self.lineedit2.setToolTip('如果學生某科目分數低於此數字會提示')
        self.lineedit2.setText('70')
        self.progress_bar_label = QLabel('處理進度')
        self.progress_bar = QProgressBar()
        self.form_layout.addRow(self.lable1, self.lineedit1)
        self.form_layout.addRow(self.lable2, self.lineedit2)
        self.form_layout.addRow(self.progress_bar_label, self.progress_bar)

        self.form_widget.setLayout(self.form_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.transcript_text)
        layout.addWidget(self.form_widget)
        layout.addWidget(self.check_btn)
        self.setLayout(layout)

        self.queue = Queue()
        self.progress_bar_thread = LoadTranscriptTask(self.queue)
        self.progress_bar_thread.finished.connect(self.show_result)

    @Slot()
    def load_transcript_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, '讀取成績單檔案', str(pathlib.Path.home()))
        if file_name:
            self.progress_bar.setRange(0, 0)
            self.queue.put([file_name, int(self.lineedit1.text()), int(self.lineedit2.text())])
            self.progress_bar_thread.start()
    
    @Slot()
    def show_result(self):
        self.transcript_text.clear()
        self.transcript_text.setText(self.queue.get())
        self.progress_bar.setRange(1, 1)


class LoadTranscriptTask(QThread):

    def __init__(self, queue, parent=None):
        super().__init__(parent)
        self.queue = queue

    def run(self):
        output = check_transcript(*self.queue.get())
        self.queue.put(output)


if __name__ == '__main__':
    app = QApplication([])
    widget = TranscriptWidget()
    widget.show()
    sys.exit(app.exec_())
