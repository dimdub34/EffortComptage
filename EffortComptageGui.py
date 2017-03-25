# -*- coding: utf-8 -*-
"""
This module contains the GUI
"""

import os
import logging
from PyQt4 import QtGui, QtCore
from random import randint
from util.utili18n import le2mtrans
from configuration import configparam as params
import EffortComptageParams as pms
from EffortComptageTexts import trans_EC
import EffortComptageTexts as texts_EC
from client.cltgui.cltguiwidgets import WExplication, WCompterebours
from twisted.internet.defer import AlreadyCalledError
import sys

logger = logging.getLogger("le2m")


class WCount(QtGui.QWidget):

    good_answer_signal = QtCore.pyqtSignal()

    def __init__(self, parent, number_id, good_answer, images, automatique):
        QtGui.QWidget.__init__(self, parent)

        self._good_answer = good_answer
        self._automatique = automatique
        self._img_question = images[0]
        self._img_true = images[1]
        self._img_false = images[2]

        # layout ===============================================================
        layout = QtGui.QHBoxLayout(self)

        self._label = QtGui.QLabel(str(number_id))
        layout.addWidget(self._label)

        self._spinbox = QtGui.QSpinBox()
        self._spinbox.setMinimum(0)
        self._spinbox.setMaximum((100))
        self._spinbox.setSingleStep(1)
        self._spinbox.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        layout.addWidget(self._spinbox)

        self._pushbutton = QtGui.QPushButton(trans_EC(u"Test"))
        self._pushbutton.clicked.connect(self._tester)
        layout.addWidget(self._pushbutton)

        self._label_img = QtGui.QLabel()
        self._label_img.setPixmap(self._img_question)
        layout.addWidget(self._label_img)

        self.adjustSize()
        self.setFixedSize(self.size())

        if automatique:
            self._spinBox.setValue(randint(0, 100))
            self._pushbutton.click()

    def _tester(self):
        if self._spinbox.value() == self._good_answer:
            self._spinbox.setEnabled(False)
            self._pushbutton.setEnabled(False)
            self._label_img.setPixmap(self._img_true)
            self.good_answer_signal.emit()
        else:
            self._label_img.setPixmap(self._img_false)

    def get_value(self):
        return self._spinbox.value()


class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._nb_good_answers = 0
        # images
        try:
            self._img_true = QtGui.QPixmap(os.path.join(params.getp("IMGDIR"),
                                                       "true.png"))
            self._img_true = self._img_true.scaledToWidth(15)
            self._img_false = QtGui.QPixmap(os.path.join(params.getp("IMGDIR"),
                                                        "false.png"))
            self._img_false = self._img_false.scaledToWidth(15)
            self._img_question = QtGui.QPixmap(os.path.join(params.getp("IMGDIR"),
                                                        "question.png"))
            self._img_question = self._img_question.scaledToWidth(15)
        except AttributeError as e:
            logger.warning(u"Error while loading images: " + e.message)

        layout = QtGui.QVBoxLayout(self)

        wexplanation = WExplication(
            text=texts_EC.get_text_explanation(),
            size=(450, 80), parent=self)
        layout.addWidget(wexplanation)

        self._compte_rebours = WCompterebours(parent=self,
                                        temps=pms.TEMPS_DECISION,
                                        actionfin=self._accept)
        layout.addWidget(self._compte_rebours)

        gridLayout = QtGui.QGridLayout()
        layout.addLayout(gridLayout)

        self._counts = {}
        counter = 1
        for col in range(pms.NB_COLUMNS):
            for row in range(pms.NB_ROWS):
                count = WCount(
                    self, counter, pms.BONNES_REPONSES[counter-1],
                    [self._img_question, self._img_true, self._img_false],
                    automatique)
                count.good_answer_signal.connect(self._add_good_answer)
                self._counts[counter] = count
                gridLayout.addWidget(count, row, col)
                counter += 1

        self.setWindowTitle(trans_EC(u"Decisions"))
        self.adjustSize()
        self.setFixedSize(self.size())

    def _add_good_answer(self):
        self._nb_good_answers += 1
        if self._nb_good_answers == len(pms.BONNES_REPONSES):
            self._accept()
                
    def reject(self):
        pass
    
    def _accept(self):
        try:
            self._compte_rebours.stop()
        except AttributeError:
            pass
        decisions = [v.get_value() for k, v in sorted(self._counts.viewitems())]
        logger.info(u"Send back {}".format(decisions))
        self.accept()
        try:
            self._defered.callback((self._nb_good_answers, decisions))
        except AlreadyCalledError: # if compte à rebours en même temps
            pass


class DConfig(QtGui.QDialog):
    def __init__(self, ecran_serveur):
        QtGui.QDialog.__init__(self, ecran_serveur)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        form_layout = QtGui.QFormLayout()
        layout.addLayout(form_layout)

        # good answers
        form_layout.setWidget(0, QtGui.QFormLayout.LabelRole,
                              QtGui.QLabel(trans_EC(u"Good answers")))
        self._lineEdit_good_ans = QtGui.QLineEdit()
        self._lineEdit_good_ans.setText(";".join(map(str, pms.BONNES_REPONSES)))
        form_layout.setWidget(0, QtGui.QFormLayout.FieldRole,
                              self._lineEdit_good_ans)

        # time
        form_layout.setWidget(1, QtGui.QFormLayout.LabelRole,
                              QtGui.QLabel(trans_EC(u"Time to fill the form")))
        self._timeEdit = QtGui.QTimeEdit()
        self._timeEdit.setTime(QtCore.QTime(pms.TEMPS_DECISION.hour,
                                            pms.TEMPS_DECISION.minute,
                                            pms.TEMPS_DECISION.second))
        form_layout.setWidget(1, QtGui.QFormLayout.FieldRole,
                              self._timeEdit)

        # payoff
        form_layout.setWidget(2, QtGui.QFormLayout.LabelRole,
                              QtGui.QLabel(trans_EC(u"Payoff")))
        self._spinbox = QtGui.QSpinBox()
        self._spinbox.setMinimum(0)
        self._spinbox.setSingleStep(1)
        self._spinbox.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spinbox.setValue(pms.GAIN)
        form_layout.setWidget(2, QtGui.QFormLayout.FieldRole,
                              self._spinbox)

        button = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        button.accepted.connect(self._accept)
        layout.addWidget(button)

        self.setWindowTitle(le2mtrans(u"Parameters"))
        self.adjustSize()

    def _accept(self):
        good_ans = map(int, self._lineEdit_good_ans.text().split(";"))
        time_to_fill = self._timeEdit.time().toPyTime()
        payoff = self._spinbox.value()
        txt_confirm = trans_EC(u"Do you confirm?") + u'\n' + \
        trans_EC(u"Good answers") + u": {}\n".format(good_ans) + \
        trans_EC(u"Time to fill the form") + u": {}\n".format(str(time_to_fill)) + \
        trans_EC(u"Payoff") + u": {}".format(payoff)
        confirm = QtGui.QMessageBox.question(
            self, le2mtrans(u"Confirmation"), txt_confirm,
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if confirm != QtGui.QMessageBox.Yes:
            return
        pms.BONNES_REPONSES = good_ans
        pms.TEMPS_DECISION = time_to_fill
        pms.GAIN = payoff
        self.accept()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    screen = GuiDecision(None, False, None)
    screen.show()
    sys.exit(app.exec_())