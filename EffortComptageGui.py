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
from client.cltgui.cltguiwidgets import WExplication, WSpinbox, WCompterebours


logger = logging.getLogger("le2m")

good_answer_signal = QtCore.pyqtSignal()


class WCount(QtGui.QWidget):
    def __init__(self, parent, number_id, good_answer, automatique):
        QtGui.QWidget.__init__(self, parent)

        self._good_answer = good_answer
        self._automatique = automatique
        self._icon_true = QtGui.QIcon(os.path.join(params.getp("IMGDIR"),
                                                   "true.png"))

        layout = QtGui.QHBoxLayout(self)

        self._decision = WSpinbox(
            label=str(number_id), minimum=0, maximum=100, interval=1,
            automatique=automatique, parent=self)
        layout.addWidget(self._decision)

        self._pushbutton = QtGui.QPushButton(trans_EC(u"Test"))
        self._pushbutton.clicked.connect(self._tester)
        layout.addWidget(self._pushbutton)

        layout.addSpacerItem(QtGui.QSpacerItem(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding, 20, 20))

        self.setWindowTitle(trans_EC(u"Décision"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if automatique:
            self._decision.ui.spinBox.setValue(randint(0, 100))
            self._pushbutton.click()

    def _tester(self):
        if self._decision.get_value() == self._good_answer:
            self._decision.setEnabled(False)
            self._pushbutton.setEnabled(False)
            self._pushbutton.setIcon(self._icon_true)
            good_answer_signal.emit()
        else:
            if not self._automatique:
                QtGui.QMessageBox.information(
                    self, trans_EC(u"Résultat test"),
                    trans_EC(u"Ce n'est pas le bon de nombre de 1"))
                return

    def get_value(self):
        return self._decision.get_value()


class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique

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
        rows = len(pms.BONNES_REPONSES) / 2
        counter = 1
        for col in range(2):
            for row in range(rows):
                count = WCount(self, counter, pms.BONNES_REPONSES[counter-1],
                               automatique)
                self._counts[counter] = count
                gridLayout.addWidget(count, row, col)
                counter += 1

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self._accept)
        layout.addWidget(buttons)

        self.setWindowTitle(trans_EC(u"Title"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if self._automatique:
            self._timer_automatique = QtCore.QTimer()
            self._timer_automatique.timeout.connect(
                buttons.button(QtGui.QDialogButtonBox.Ok).click)
            self._timer_automatique.start(7000)
                
    def reject(self):
        pass
    
    def _accept(self):
        try:
            self._timer_automatique.stop()
        except AttributeError:
            pass
        decisions = [v.get_value() for k, v in sorted(self._counts.viewitems())]
        good_rep = 0
        for i, val in enumerate(pms.BONNES_REPONSES):
            if decisions[i] == val:
                good_rep += 1
        if not self._automatique:
            confirmation = QtGui.QMessageBox.question(
                self, le2mtrans(u"Confirmation"),
                le2mtrans(u"Do you confirm your choice?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
            if confirmation != QtGui.QMessageBox.Yes: 
                return
        logger.info(u"Send back {}".format(decisions))
        self.accept()
        self._defered.callback((good_rep, decisions))
