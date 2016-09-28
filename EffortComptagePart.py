# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from twisted.internet import defer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey
from server.servbase import Base
from server.servparties import Partie
from util.utiltools import get_module_attributes
import EffortComptageParams as pms


logger = logging.getLogger("le2m")


class PartieEC(Partie):
    __tablename__ = "partie_EffortComptage"
    __mapper_args__ = {'polymorphic_identity': 'EffortComptage'}
    partie_id = Column(Integer, ForeignKey('parties.id'), primary_key=True)
    repetitions = relationship('RepetitionsEC')

    def __init__(self, le2mserv, joueur):
        super(PartieEC, self).__init__(
            nom="EffortComptage", nom_court="EC",
            joueur=joueur, le2mserv=le2mserv)
        self.EC_gain_ecus = 0
        self.EC_gain_euros = 0

    @defer.inlineCallbacks
    def configure(self):
        logger.debug(u"{} Configure".format(self.joueur))
        yield (self.remote.callRemote("configure", get_module_attributes(pms)))
        self.joueur.info(u"Ok")

    @defer.inlineCallbacks
    def newperiod(self, period):
        """
        Create a new period and inform the remote
        If this is the first period then empty the historic
        :param periode:
        :return:
        """
        logger.debug(u"{} New Period".format(self.joueur))
        self.currentperiod = RepetitionsEC(period)
        self.le2mserv.gestionnaire_base.ajouter(self.currentperiod)
        self.repetitions.append(self.currentperiod)
        yield (self.remote.callRemote("newperiod", period))
        logger.info(u"{} Ready for period {}".format(self.joueur, period))

    @defer.inlineCallbacks
    def display_decision(self):
        """
        Display the decision screen on the remote
        Get back the decision
        :return:
        """
        logger.debug(u"{} Decision".format(self.joueur))
        debut = datetime.now()
        self.currentperiod.EC_bonnes_reponses, reponses = yield(
            self.remote.callRemote("display_decision"))
        self.currentperiod.EC_decisiontime = (datetime.now() - debut).seconds
        self.joueur.info(u"{} - {}".format(
            self.currentperiod.EC_bonnes_reponses, reponses))
        self.joueur.info(u"{}".format(self.currentperiod.EC_decision))
        self.joueur.remove_waitmode()

    def compute_periodpayoff(self):
        """
        Compute the payoff for the period
        :return:
        """
        logger.debug(u"{} Period Payoff".format(self.joueur))
        self.currentperiod.EC_periodpayoff = pms.GAIN if \
            self.currentperiod.EC_bonnes_reponses == len(pms.BONNES_REPONSES) \
            else 0

        # cumulative payoff since the first period
        if self.currentperiod.EC_period < 2:
            self.currentperiod.EC_cumulativepayoff = \
                self.currentperiod.EC_periodpayoff
        else: 
            previousperiod = self.periods[self.currentperiod.EC_period - 1]
            self.currentperiod.EC_cumulativepayoff = \
                previousperiod.EC_cumulativepayoff + \
                self.currentperiod.EC_periodpayoff

        # we store the period in the self.periodes dictionnary
        self.periods[self.currentperiod.EC_period] = self.currentperiod

        logger.debug(u"{} Period Payoff {}".format(
            self.joueur,
            self.currentperiod.EC_periodpayoff))

    @defer.inlineCallbacks
    def display_summary(self, *args):
        """
        Send a dictionary with the period content values to the remote.
        The remote creates the text and the history
        :param args:
        :return:
        """
        logger.debug(u"{} Summary".format(self.joueur))
        yield(self.remote.callRemote(
            "display_summary", self.currentperiod.todict()))
        self.joueur.info("Ok")
        self.joueur.remove_waitmode()

    @defer.inlineCallbacks
    def compute_partpayoff(self):
        """
        Compute the payoff for the part and set it on the remote.
        The remote stores it and creates the corresponding text for display
        (if asked)
        :return:
        """
        logger.debug(u"{} Part Payoff".format(self.joueur))

        self.EC_gain_ecus = self.currentperiod.EC_cumulativepayoff
        self.EC_gain_euros = float(self.EC_gain_ecus) * float(pms.TAUX_CONVERSION)
        yield (self.remote.callRemote(
            "set_payoffs", self.EC_gain_euros, self.EC_gain_ecus))

        logger.info(u'{} Payoff ecus {} Payoff euros {:.2f}'.format(
            self.joueur, self.EC_gain_ecus, self.EC_gain_euros))


class RepetitionsEC(Base):
    __tablename__ = 'partie_EffortComptage_repetitions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    partie_partie_id = Column(
        Integer,
        ForeignKey("partie_EffortComptage.partie_id"))

    EC_period = Column(Integer)
    EC_treatment = Column(Integer)
    EC_group = Column(Integer)
    EC_decision = Column(Integer)
    EC_bonnes_reponses = Column(Integer)
    EC_decisiontime = Column(Integer)
    EC_periodpayoff = Column(Float)
    EC_cumulativepayoff = Column(Float)

    def __init__(self, period):
        self.EC_treatment = pms.TREATMENT
        self.EC_period = period
        self.EC_decisiontime = 0
        self.EC_periodpayoff = 0
        self.EC_cumulativepayoff = 0

    def todict(self, joueur=None):
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if joueur:
            temp["joueur"] = joueur
        return temp

