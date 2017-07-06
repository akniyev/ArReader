import sys

from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
import requests
import html
import csv


class Translation:
    def __init__(self, form: str, variants: [str]):
        self.form : str = form
        self.variants : [str] = variants


class TranslationCsv:
    def __init__(self, form: str, translation: str):
        self.form = form
        self.translation = translation


class TranslatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.vbox = QVBoxLayout()
        self.textView = QLineEdit("كلام")
        self.tag_text_view = QLineEdit("ar_")
        self.btn_translate = QPushButton("Translate!")
        self.btn_export = QPushButton("Export as csv...")
        self.vbox_button = QVBoxLayout()
        self.translation_controls = []
        self.timer = QTimer()
        self.translations_to_export = []

        font: QFont = self.textView.font()
        font.setPointSizeF(20)
        self.textView.setFont(font)

        self.vbox.addWidget(self.textView)
        self.vbox.addWidget(self.btn_translate)
        self.vbox.addLayout(self.vbox_button)
        self.vbox.addWidget(self.btn_export)
        self.vbox.addWidget(self.tag_text_view)

        self.setLayout(self.vbox)
        self.btn_translate.pressed.connect(self.translate_action)

        # QApplication.clipboard().changed.connect(self.clipboard_changed)
        self.timer.setInterval(200)
        self.timer.start()
        self.current_clipboard = ""
        self.textView.setText(self.current_clipboard)
        self.timer.timeout.connect(self.timeout)
        self.btn_export.pressed.connect(self.export_csv)

    def timeout(self):
        txt = QApplication.clipboard().text()
        if len(txt.split(' ')) != 1:
            return

        if txt != self.current_clipboard:
            self.current_clipboard = txt
            self.textView.setText(txt)
            self.translate_action()

        g = self.geometry()
        self.setGeometry(g.x(), g.y(), 500, 10)

    def export_csv(self):
        filename = QFileDialog.getSaveFileName()[0]
        tag = self.tag_text_view.text()

        if filename == "" or tag == "":
            return

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Arabic', 'Russian', 'tag'])
            for translation in self.translations_to_export:
                writer.writerow([translation.form, translation.translation, tag])

    def add_action(self):
        id : int = self.sender().monkeyNumber
        controls = self.translation_controls[id]
        lbl : QLabel = controls[0]
        print(lbl.fontInfo())
        form = lbl.text()
        variants = ""
        for c in controls[1:]:
            cb : QCheckBox = c
            if cb.isChecked():
                variants += cb.text() + ", "
        variants = variants[:-2]

        if form == "" or variants == "":
            return

        csv_item = TranslationCsv(form, variants)
        self.translations_to_export.append(csv_item)

    def translate_action(self):
        for i in reversed(range(tw.vbox_button.count())):
            l = tw.vbox_button.itemAt(i).layout()
            for j in reversed(range(l.count())):
                l.itemAt(j).widget().setParent(None)
            l.setParent(None)
        self.translation_controls = []

        if self.textView.text() == "":
            return

        translations = self.translation_request(tw.textView.text())
        print(tw.textView.text())

        i = 0
        for translation in translations:
            controls = []
            btn = QPushButton("Add")
            btn.pressed.connect(self.add_action)
            btn.monkeyNumber = i
            lbl = QLabel(translation.form)
            font: QFont = lbl.font()
            font.setPointSizeF(20)
            lbl.setFont(font)
            controls.append(lbl)
            hbox = QHBoxLayout()
            hbox.addWidget(lbl)
            for variant in translation.variants:
                cb = QCheckBox(variant)
                hbox.addWidget(cb)
                controls.append(cb)
            hbox.addWidget(btn)
            tw.vbox_button.addLayout(hbox)
            self.translation_controls.append(controls)
            i += 1


    def translation_request(self, word: str) -> [Translation]:
        request_url = 'http://api.aratools.net/dict-service?query={"word": "' + word + '", "dictionary": "AR-EN-WORD-DICTIONARY"}&format=json'

        r = requests.get(request_url)
        jsons = r.json()['result']

        result = []

        for json in jsons:
            solution = json['solution']
            form = html.unescape(solution['vocForm'])
            translations = solution['niceGloss'].split(';')
            t = Translation(form, translations)
            result.append(t)

        return result


if __name__ == '__main__':
    app = QApplication(sys.argv)

    tw = TranslatorWindow()

    # for i in range(10):
    #     tw.vbox_button.addWidget(QPushButton("translation"))

    tw.show()

    sys.exit(app.exec_())