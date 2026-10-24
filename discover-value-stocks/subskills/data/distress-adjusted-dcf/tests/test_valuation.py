import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from valuation import damodaran,cds_hazard_approx,survival
from enterprise import enterprise_dcf
from math import exp

class Tests(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(damodaran(100,20,0),100)
        self.assertEqual(damodaran(100,20,1),20)
        self.assertEqual(damodaran(100,20,.25),80)
    def test_invalid(self):
        with self.assertRaises(ValueError): damodaran(100,0,1.2)
        with self.assertRaises(ValueError): cds_hazard_approx(300,1)
        with self.assertRaises(ValueError): survival([-1],[1])
    def test_hazard(self):
        self.assertAlmostEqual(cds_hazard_approx(300,.4),.05)
        self.assertAlmostEqual(survival([.05,.05],[1,1])[-1],exp(-.1))
    def test_no_default(self):
        self.assertAlmostEqual(enterprise_dcf([10,10],[.1,.1],[0,0],[1,1],100,[0,0]),10/1.1+110/1.1**2)
    def test_monotone(self):
        a=enterprise_dcf([10],[.05],[.01],[1],100,[10])
        b=enterprise_dcf([10],[.05],[.5],[1],100,[10])
        self.assertLess(b,a)
    def test_bad_array(self):
        with self.assertRaises(ValueError): enterprise_dcf([10],[.1],[],[1],100,[0])

class NumericValidationTests(unittest.TestCase):
    def calls_for_each_field(self, value):
        for index in range(3):
            args = [100, 20, .25]
            args[index] = value
            yield 'damodaran', index, lambda args=args: damodaran(*args)
        for index in range(2):
            args = [300, .4]
            args[index] = value
            yield 'cds', index, lambda args=args: cds_hazard_approx(*args)
        for index in range(2):
            args = [[.05], [1]]
            args[index] = [value]
            yield 'survival', index, lambda args=args: survival(*args)
        for index in range(6):
            args = [[10], [.1], [.05], [1], 100, [10]]
            args[index] = value if index == 4 else [value]
            yield 'enterprise', index, lambda args=args: enterprise_dcf(*args)

    def test_nonfinite_in_every_numeric_field(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            for name, index, call in self.calls_for_each_field(value):
                with self.subTest(function=name, field=index, value=value):
                    with self.assertRaises(ValueError):
                        call()

    def test_wrong_types_in_every_numeric_field(self):
        for value in (None, '10', True, False, 1+0j, [], {}):
            for name, index, call in self.calls_for_each_field(value):
                with self.subTest(function=name, field=index, value=value):
                    with self.assertRaises(TypeError):
                        call()

    def test_invalid_containers(self):
        for value in (None, 1, '1', b'1', {'a': 1}, iter([1])):
            for call in (lambda: survival(value, [1]),
                         lambda: survival([0], value)):
                with self.subTest(value=value):
                    with self.assertRaises(TypeError):
                        call()
            for index in (0, 1, 2, 3, 5):
                args = [[10], [.1], [0], [1], 100, [0]]
                args[index] = value
                with self.subTest(value=value, field=index):
                    with self.assertRaises(TypeError):
                        enterprise_dcf(*args)

    def test_reported_regressions(self):
        with self.assertRaises(ValueError):
            damodaran(100, float('nan'), .25)
        with self.assertRaises(ValueError):
            cds_hazard_approx(float('nan'), .4)
        with self.assertRaises(ValueError):
            enterprise_dcf([10], [float('inf')], [0], [1], 100, [0])

    def test_zero_and_negative_values(self):
        self.assertEqual(damodaran(-100, 0, 0), -100)
        self.assertEqual(damodaran(-100, 0, 1), 0)
        self.assertEqual(cds_hazard_approx(0, 0), 0)
        self.assertEqual(survival((0, 0), (.5, 2)), [1, 1])
        self.assertEqual(enterprise_dcf([-10], [0], [0], [1], -100, [0]), -110)
        self.assertEqual(enterprise_dcf([0], [0], [0], [1], 0, [0]), 0)
        self.assertAlmostEqual(enterprise_dcf([10], [-.5], [0], [1], 0, [0]), 20)

    def test_fractional_period_and_recovery(self):
        s = exp(-.1*.5)
        expected = (s*(-10)+(1-s)*20+s*100)/(1.1**.5)
        self.assertAlmostEqual(enterprise_dcf([-10], [.1], [.1], [.5], 100, [20]), expected)
        self.assertAlmostEqual(cds_hazard_approx(1, 1-1e-10), 1/10000/(1-(1-1e-10)))

    def test_invalid_domains(self):
        for args in ((100, -1, .2), (100, 0, -.01), (100, 0, 1.01)):
            with self.assertRaises(ValueError): damodaran(*args)
        for args in ((-1, .4), (10, -.01), (10, 1)):
            with self.assertRaises(ValueError): cds_hazard_approx(*args)
        for args in (([-1], [1]), ([0], [0]), ([0], [-1]), ([], []), ([0, 0], [1])):
            with self.assertRaises(ValueError): survival(*args)
        for index, value in ((1, [-1]), (1, [-2]), (5, [-1])):
            args = [[10], [.1], [0], [1], 100, [0]]
            args[index] = value
            with self.assertRaises(ValueError): enterprise_dcf(*args)
        with self.assertRaises(ValueError): enterprise_dcf([], [], [], [], 0, [])

    def test_finite_inputs_with_nonfinite_intermediates(self):
        for call in (
            lambda: survival([1e308], [2]),
            lambda: survival([1e308, 1e308], [1, 1]),
            lambda: enterprise_dcf([10], [1e308], [0], [2], 100, [0]),
            lambda: enterprise_dcf([1e308], [-.9], [0], [2], 0, [0]),
            lambda: enterprise_dcf([1e308], [0], [0], [1], 1e308, [0]),
            lambda: enterprise_dcf([1e308, 1e308], [0, 0], [0, 0], [1, 1], 0, [0, 0]),
            lambda: enterprise_dcf([1], [-.9], [0], [1000], 0, [0]),
            lambda: enterprise_dcf([1, 1], [1e200, 1e200], [0, 0], [1, 1], 0, [0, 0]),
        ):
            with self.subTest(call=call):
                with self.assertRaises(ValueError): call()

    def test_large_finite_hazard_survival_underflow_is_valid(self):
        self.assertEqual(survival([1000], [1]), [0])
        self.assertEqual(enterprise_dcf([10], [0], [1000], [1], 100, [20]), 20)

    def test_oversized_integer_is_explicit_error(self):
        for name, index, call in self.calls_for_each_field(10**1000):
            with self.subTest(function=name, field=index):
                with self.assertRaises(ValueError): call()


if __name__=='__main__': unittest.main()
