# -*- coding: utf-8 -*-
"""
test_build_chain
================
Test FSIC build chain from specification through to class generation.

The specification in `test_build_chain_sim()` is of Model *SIM* from:

Godley, W., Lavoie, M. (2007),
*Monetary economics: An integrated approach to
credit, money, income, production and wealth*,
Palgrave Macmillan

The equation in `test_build_chain_re()` is from Section 13.3 of:

Fair, R. C. (2016),
'The US Model Workbook',
January 30, 2016

"""

from FSIC.parser.wrappers import read_python
from FSIC.build.model import build_model


TEMPLATE = '''\
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name}
{underline}
FSIC model class generated by `FSIC.build_model()`.

"""

import FSIC


class {name}(FSIC.Model):
    """FSIC model class.

    """

{static}


    def _solve_python_iteration(self, row):
{system}
'''


def test_build_chain_sim():
    xp = TEMPLATE.format(
        name='SIM', underline='===',
        static='''\
    VARIABLES = ['C_s', 'C_d', 'G_s', 'G_d', 'T_s', 'T_d', 'N_s', 'N_d', 'YD', 'H_h', 'H_s', 'Y']
    PARAMETERS = ['W', 'theta', 'alpha_1', 'alpha_2']
    AUTOMATIC = []
    ERRORS = []

    CONVERGENCE_VARIABLES = ['C_s', 'C_d', 'G_s', 'T_s', 'T_d', 'N_s', 'N_d', 'YD', 'H_h', 'H_s', 'Y']

    EXOGENOUS_VARIABLES = ['G_d']

    START_OFFSET = 1
    END_OFFSET = 0

    VERSION = '0.1.0.dev'\
''', system='''\
        self.G_s.values[row] = self.G_d.values[row]

        self.C_d.values[row] = self.alpha_1.values[row] * self.YD.values[row] + self.alpha_2.values[row] * self.H_h.values[row-1]
        self.C_s.values[row] = self.C_d.values[row]
        self.Y.values[row] = self.C_s.values[row] + self.G_s.values[row]
        self.N_d.values[row] = self.Y.values[row] / self.W.values[row]
        self.N_s.values[row] = self.N_d.values[row]
        self.YD.values[row] = self.W.values[row] * self.N_s.values[row] - self.T_s.values[row]
        self.T_d.values[row] = self.theta.values[row] * self.W.values[row] * self.N_s.values[row]
        self.T_s.values[row] = self.T_d.values[row]

        self.H_h.values[row] = self.H_h.values[row-1] + self.YD.values[row] - self.C_d.values[row]
        self.H_s.values[row] = self.H_s.values[row-1] + self.G_d.values[row] - self.T_d.values[row]\
''')

    specification = '''\
C_s = C_d
G_s = G_d
T_s = T_d
N_s = N_d
YD = {W} * N_s - T_s
T_d = {theta} * {W} * N_s
C_d = {alpha_1} * YD + {alpha_2} * H_h[-1]
H_s = H_s[-1] + G_d - T_d
H_h = H_h[-1] + YD - C_d
Y = C_s + G_s
N_d = Y / {W}
'''
    script = build_model(read_python(specification), output='script', name='SIM')
    assert script == xp

def test_build_chain_re():
    xp = TEMPLATE.format(
        name='RE', underline='==',
        static='''\
    VARIABLES = ['RB', 'RS']
    PARAMETERS = []
    AUTOMATIC = []
    ERRORS = []

    CONVERGENCE_VARIABLES = ['RB']

    EXOGENOUS_VARIABLES = ['RS']

    START_OFFSET = 0
    END_OFFSET = 6

    VERSION = '0.1.0.dev'\
''', system='''\
        self.RB.values[row] = (self.RS.values[row] + self.RS.values[row+1] + self.RS.values[row+2] + self.RS.values[row+3] + self.RS.values[row+4] + self.RS.values[row+5] + self.RS.values[row+6]) / 7\
''')

    specification = 'RB = (RS + RS[1] + RS[2] + RS[3] + RS[4] + RS[5] + RS[6]) / 7'''
    script = build_model(read_python(specification), output='script', name='RE')
    assert script == xp


if __name__ == '__main__':
    nose.runmodule()
