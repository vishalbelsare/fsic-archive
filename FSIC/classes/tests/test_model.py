# -*- coding: utf-8 -*-
"""
test_model
==========
Test FSIC `Model` class.

"""

from pandas import PeriodIndex
from pandas import DataFrame
from pandas.util.testing import assert_frame_equal

import nose
from nose.tools import raises

from FSIC.classes.model import Model


class TestModel(Model):
    VARIABLES = list('YCIGXM')
    START_OFFSET = 5
    END_OFFSET = 5

class TestModelConv(TestModel):
    CONVERGENCE_VARIABLES = list('Y')

    def _solve_python_iteration(self, row):
        self.Y.values[row] = (self.C.values[row] +
                              self.I.values[row] +
                              self.G.values[row] +
                              self.X.values[row] -
                              self.M.values[row])


def test_initialise_period_index():
    xp = DataFrame({'Y': 0.0, 'C': 0.0, 'I': 0.0, 'G': 0.0, 'X': 0.0, 'M': 0.0,
                    'iterations': -1, 'converged': False, 'status': '-'},
                   index=PeriodIndex(start=1990, end=2020))

    model = TestModel(1990, 2020)
    assert_frame_equal(model.data.reindex(columns=xp.columns), xp)

    model.initialise(solve_from=1995, solve_to=2015)
    assert_frame_equal(model.data.reindex(columns=xp.columns), xp)

    model.initialise(1990, 2020, variables=list('YCIG'))
    assert_frame_equal(
        model.data.reindex(columns=xp.drop(list('XM'), axis=1).columns),
        xp.drop(list('XM'), axis=1))

    model.initialise(1990, 2020, parameters=list('YCIG'))
    assert_frame_equal(
        model.data.reindex(columns=xp.drop(list('XM'), axis=1).columns),
        xp.drop(list('XM'), axis=1))

    model.initialise(1990, 2020, errors=list('YCIG'))
    assert_frame_equal(
        model.data.reindex(columns=xp.drop(list('XM'), axis=1).columns),
        xp.drop(list('XM'), axis=1))

    model.initialise(data=xp)
    assert_frame_equal(model.data.reindex(columns=xp.columns), xp)

    model.initialise(1990, 2020, data=xp.ix[1995:2000, :])
    assert_frame_equal(model.data.reindex(columns=xp.columns), xp)

def test_initialise_integer_index():
    xp = DataFrame({'Y': 0.0, 'C': 0.0, 'I': 0.0, 'G': 0.0, 'X': 0.0, 'M': 0.0,
                    'iterations': -1, 'converged': False, 'status': '-'},
                   index=range(-10, 11))

    model = TestModel(-10, 10)
    assert_frame_equal(model.data.reindex(columns=xp.columns), xp)

    model.initialise(-10, 10, convergence_variables=['Y'])
    assert_frame_equal(model.data.reindex(columns=xp.columns), xp)

    model = TestModelConv(solve_from=-5, solve_to=5)
    assert_frame_equal(model.data.reindex(columns=xp.columns), xp)

    model = Model(solve_from=1, solve_to=1000)
    assert list(model.data.index.values) == list(range(1, 1001))

    model.initialise(data=xp)
    assert_frame_equal(model.data.reindex(columns=xp.columns), xp)

def test_initialise_integer_index_with_zero():
    model = Model(0, 5)
    assert list(model.data.index) == list(range(6))

    model = Model(-5, 0)
    assert list(model.data.index) == list(range(-5, 1))

    model = Model(solve_from=0, solve_to=10)
    assert list(model.data.index) == list(range(11))

    model = Model(solve_from=-10, solve_to=0)
    assert list(model.data.index) == list(range(-10, 1))


@raises(ValueError)
def test_initialise_errors_start():
    model = Model().initialise(end=10)

@raises(ValueError)
def test_initialise_errors_end():
    model = Model().initialise(start=-10)


def test_property_get_set():
    model = Model(0, 10, variables=list('YCIG'))

    model.Y = 10
    assert model.Y.sum() == 110

    model.Y[5] = 50
    assert model.Y.sum() == 150

    model.G[3:5] = 20
    assert model.G.sum() == 40

@raises(RuntimeError)
def test_property_del_error():
    model = Model(0, 10, variables=list('YCIG'))
    del model.Y


@raises(RuntimeError)
def test_solve_before_initialise():
    model = Model()
    model.solve()

@raises(ValueError)
def test_solve_period_argument_error():
    model = Model(0, 10)
    model.solve(first=2, last=8, single=5)

def test_solve():
    model = TestModelConv('2000Q1', '2005Q4')
    model.G = 20
    model.M = 10
    model.solve(single='2000Q1')
    model.solve(single='2005Q4', verbosity=1)
    model.solve()
    model.solve('2000Q2', '2000Q4', verbosity=1)
    assert sum(model.Y * model.iterations) == 380


if __name__ == '__main__':
    nose.runmodule()