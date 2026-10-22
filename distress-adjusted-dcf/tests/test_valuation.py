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

if __name__=='__main__': unittest.main()
