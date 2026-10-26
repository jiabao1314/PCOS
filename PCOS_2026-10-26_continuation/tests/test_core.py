"""Analytical fixtures only. These are not GBD observations or study results."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from core import standardize,pooled_rate,shapley,segmented_trend

class CoreTests(unittest.TestCase):
    def test_standardization_and_pooling(self):
        self.assertAlmostEqual(standardize([10,30],[2,1]),50/3)
        self.assertAlmostEqual(pooled_rate([2,30],[100,10000]),32/10100*100000)
        self.assertNotAlmostEqual(pooled_rate([2,30],[100,10000]),(2000+300)/2)
    def test_scale_only(self):
        v,total=shapley([100,200],[200,400],[.1,.2],[.1,.2])
        self.assertAlmostEqual(v['population_size'],50)
        self.assertAlmostEqual(v['age_composition'],0)
        self.assertAlmostEqual(v['age_specific_prevalence'],0)
        self.assertAlmostEqual(total,50)
    def test_shapley_reversal_and_additivity(self):
        a,b,p,q=np.array([100.,220,60]),np.array([140.,200,120]),np.array([.02,.03,.01]),np.array([.04,.02,.03])
        f,total=shapley(a,b,p,q); r,back=shapley(b,a,q,p)
        self.assertAlmostEqual(sum(f.values()),np.dot(b,q)-np.dot(a,p))
        for key in f:self.assertAlmostEqual(f[key],-r[key])
        self.assertAlmostEqual(total,-back)
    def test_log_linear(self):
        years=np.arange(1990,2024)
        fit=segmented_trend(years,100*np.exp(.02*(years-1990)))
        self.assertEqual(fit['knots'],[])
        self.assertAlmostEqual(fit['aapc_percent'],100*np.expm1(.02))
    def test_piecewise_and_zero_rejection(self):
        years=np.arange(1990,2024)
        rates=np.exp(2+.02*(years-1990)-.05*np.maximum(years-2005,0))
        fit=segmented_trend(years,rates)
        self.assertIn(2005,fit['knots'])
        with self.assertRaises(ValueError):segmented_trend(years,np.zeros(len(years)))

if __name__=='__main__':unittest.main()
