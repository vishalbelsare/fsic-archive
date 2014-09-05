# -*- coding: utf-8 -*-
"""
___NAME___
___MODULE_DOCSTRING___

___FSIC_VERSION___

"""


import argparse
import os

import numpy as np
from pandas import Series, DataFrame

from fsic import __version__ as version

from fsic.model.model import Model


# Define ___MODEL___ class
class ___MODEL___(Model):
    """___SHORT_DESCRIPTION___

    ___LONG_DESCRIPTION___

    """

    def __init__(self):
        Model.__init__(self)
        ___MODEL_VERSION___

    def initialise(self, span, past=[], default=0):
        """Initialise the model for solution.

        Parameters
        ==========
        span : list
            The index to set the principal span of the model (used as part of
            the index for individual variable Series objects)
        past : list
            The index to set the preceding span of the model (may be necessary
            to supply enough lags for dynamic models; added to the beginning of
            `span`)
        default : float
            Value to initialise variable Series objects with

        Notes
        =====
        Variable-initialisation statements take the form (using the variable C_d
        as an example):
            self.C_d = Series(default, index=self.full_span, dtype=np.float64)

        """
        # Store function arguments
        self.span = span
        self.past = past
        # Form full span and initialise `iter`
        self.full_span = past + span
        self.iter = Series(default, index=self.full_span, dtype=np.float64)
        # Initialise model variables
        ___INITIALISE___
        # Update solution state variables
        self.initialised = True
        self.solved = False

    def solve_equations(self, period):
        """Solve the model equations for `period`.

        Parameters
        ==========
        period : Series index
            The identifier of the period to solve

        Notes
        =====
        Equation statements take the form (usng the variable C_s as an example):
            self.C_s[period] = self.C_d[period]

        """
        ___SOLVE_EQUATIONS___

    def get_endogenous_variable_values(self, period):
        """Return the current values of the endogenous variables.

        Parameters
        ==========
        period : Series index
            The identifier of the period to solve

        Returns
        =======
        values : pandas Series
            Endogenous variable values for the current `period`

        Notes
        =====
        Endogenous variable value-extraction statements take the form (using the
        variable C_d as an example):
            values['C_d'] = self.C_d[period]

        """
        values = {}
        ___GET_ENDOGENOUS_VARIABLE_VALUES___
        return Series(values)

    def get_results(self):
        """Return the results from the model solution.

        Parameters
        ==========
        N/A

        Returns
        =======
        results : DataFrame
            Solution results

        Notes
        =====
        The code to form a results DataFrame takes the following form:
            results = DataFrame({
                'C_d': self.C_d,
                'C_s': self.C_s,})

        """
        ___GET_RESULTS___
        results['iter'] = self.iter
        return results


# Create command-line argument parser
parser = argparse.ArgumentParser(
    description='___SHORT_DESCRIPTION___',
    fromfile_prefix_chars='@',
    formatter_class=argparse.RawDescriptionHelpFormatter)

model_version = SIM()
parser.add_argument(
    '-V', '--version',
    action='version',
    version='''\
Model version: %s
Built under FSIC version: %s
FSIC version installed: %s
''' % (model_version.VERSION, model_version.FSIC_BUILD, version))
del model_version

parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='print detailed solution output (not yet implemented)')

parser.add_argument(
    '-o', '--output',
    nargs='+',
    metavar='OUTPUT',
    default=None,
    type=str,
    required=False,
    help='list of output files for model results')

parser.add_argument(
    '-D', '--define',
    action='append',
    nargs='+',
    metavar='PARAMETER',
    default=None,
    type=str,
    required=False,
    help='set (time-invariant) model parameters')
parser.add_argument(
    '--set',
    action='append',
    nargs='+',
    metavar='EXPRESSION',
    default=None,
    type=str,
    required=False,
    help='set (time-varying) model variables prior to run')

parser.add_argument(
    '--span',
    nargs=2,
    metavar='PERIOD',
    default=None,
    type=int,
    required=False,
    help='set the start and end periods of the model run')
parser.add_argument(
    '--past',
    metavar='PERIOD',
    default=None,
    type=int,
    required=False,
    help='set the first historical period of the model run')


# Import get_ipython() from IPython as a check for an interactive shell
try:
    from IPython import get_ipython
except:
    def get_ipython():
        return None

if __name__ == '__main__' and get_ipython() == None:
    # Parse arguments
    args = parser.parse_args()
    # Setup model
    model = ___MODEL___()
    if args.span:
        start, end = args.span
        span = list(range(start, end + 1))
        if args.past:
            past = args.past
            if past >= start:
                raise ValueError(
                    'First historical period (`past`) is %d, when it must '
                    'be *before* the first solution period (`start`) of %d'
                    % (past, start))
            past = list(range(past, start))
        else:
            past = []
        model.initialise(span=span, past=past)
    if args.define:
        parameters = []
        for a in args.define:
            for d in a:
                d = d.split('=')
                if len(d) != 2:
                    raise ValueError(
                        'Error in `define` argument: \'%s\'; '
                        'must be a parameter name and value '
                        'separated by an equals sign e.g. W=1' % (d))
                p, v = d
                c = 'model.%s.ix[:] = %f' % (p, float(v))
                parameters.append(c)
        parameters = '\n'.join(parameters)
        exec(parameters)
    if args.set:
        expressions = []
        for a in args.set:
            for x in a:
                x = 'model.' + x.replace('[', '.ix[')
                expressions.append(x)
        expressions = '\n'.join(expressions)
        exec(expressions)
    # Solve
    if model.initialised:
        model.solve()
    # Write results
    if args.output is not None:
        if model.initialised:
            results = model.get_results()
            for o in args.output:
                if o.endswith('.csv'):
                    results.to_csv(o)
                else:
                    ext = os.path.splitext(o)[1]
                    raise ValueError(
                        'Unrecognised output file extension: \'%s\'' % (ext))
        else:
            raise ValueError(
                'Model not solved: no results to save')