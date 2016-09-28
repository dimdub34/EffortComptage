# -*- coding: utf-8 -*-
"""
This module contains the texts of the part (server and remote)
"""

from util.utiltools import get_pluriel
import EffortComptageParams as pms
from util.utili18n import le2mtrans
import os
import configuration.configparam as params
import gettext
import logging

logger = logging.getLogger("le2m")
localedir = os.path.join(params.getp("PARTSDIR"), "EffortComptage", "locale")
try:
    trans_EC = gettext.translation(
      "EffortComptage", localedir, languages=[params.getp("LANG")]).ugettext
except IOError:
    logger.critical(u"Translation file not found")
    trans_EC = lambda x: x  # if there is an error, no translation


def get_histo_head():
    return [le2mtrans(u"Period"), le2mtrans(u"Decision"),
             le2mtrans(u"Period\npayoff"), le2mtrans(u"Cumulative\npayoff")]


def get_text_explanation():
    return trans_EC(u"")


def get_text_summary(period_content):
    txt = trans_EC(u"Summary text")
    return txt


