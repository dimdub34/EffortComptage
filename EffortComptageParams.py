# -*- coding: utf-8 -*-
"""=============================================================================
This modules contains the variables and the parameters.
Do not change the variables.
Parameters that can be changed without any risk of damages should be changed
by clicking on the configure sub-menu at the server screen.
If you need to change some parameters below please be sure of what you do,
which means that you should ask to the developer ;-)
============================================================================="""

from datetime import time

# variables --------------------------------------------------------------------
TREATMENTS = {0: "baseline"}

# parameters -------------------------------------------------------------------
TREATMENT = 0
TAUX_CONVERSION = 1
NOMBRE_PERIODES = 0
TAILLE_GROUPES = 0
GROUPES_CHAQUE_PERIODE = False
MONNAIE = u"None"

BONNES_REPONSES = [4, 5, 20, 22, 31, 41, 51, 69, 82, 95]  # mettre une liste
TEMPS_DECISION = time(0, 15, 0) # heures, minutes, secondes
GAIN = 10


def get_treatment(code_or_name):
    if type(code_or_name) is int:
        return TREATMENTS.get(code_or_name, None)
    elif type(code_or_name) is str:
        for k, v in TREATMENTS.viewitems():
            if v.lower() == code_or_name.lower():
                return k
    return None
