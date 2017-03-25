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
PAPER = 0
SCREEN = 1
TREATMENTS_NAMES = {PAPER: "PAPER", SCREEN: "SCREEN"}

# parameters -------------------------------------------------------------------
TREATMENT = SCREEN
TAUX_CONVERSION = 1
NOMBRE_PERIODES = 0
TAILLE_GROUPES = 0
MONNAIE = u"euro"

BONNES_REPONSES = [4, 5, 20, 22, 31, 41, 51, 69, 82, 95]  # mettre une liste
NB_ROWS, NB_COLUMNS = 5, 2
TEMPS_DECISION = time(0, 15, 0) # heures, minutes, secondes
GAIN = 10

