import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class WordSelectorWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setText("I know this is an older thread, but it fits. I am trying to do something similar in QT4.5.")
    #     self.selectionChanged.connect(self.onSelect)
    #
    # def onSelect(self):
    #     print(self.textCursor().selectedText())

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        super().mouseReleaseEvent(e)
        text = self.textCursor().selectedText()
        if len(text) > 0 and len(text) < 50 and len(text.split(' ')) == 1:
            print(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    wsw = WordSelectorWidget()

    wsw.show()

    sys.exit(app.exec_())