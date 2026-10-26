"""Temporary synthetic fixtures test calculations and rejection paths only."""
import json,sys,tempfile,unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import STUDY,load_validate,run

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='pcos_unit_fixture_')
        cls.folder=Path(cls.tmp.name)
        rows=[];pop=[]
        for c,country in enumerate(STUDY['countries']):
            for year in range(1990,2022):
                for a,age in enumerate(STUDY['ages']):
                    population=100000*(c+1)*(1+.005*(year-1990))*(a+1)
                    pop.append(['GBD 2021',c+1,year,2,a+1,population])
                    for k,cause in enumerate(STUDY['causes']):
                        for m,measure in enumerate(STUDY['measures']):
                            rate=10*(c+1)*(a+1)*(k+1)*(.01 if m else 1)*np.exp(.001*(year-1990))
                            for metric in ['Number','Rate']:
                                val=rate if metric=='Rate' else rate/100000*population
                                rows.append(['GBD 2021',c+1,year,2,a+1,k+1,1,'Total',measure,metric,country,age,'Female',cause,'Infertility',val,.9*val,1.1*val])
        from analyze import REQUIRED
        pd.DataFrame(rows,columns=REQUIRED).to_csv(cls.folder/'burden.csv',index=False)
        pd.DataFrame(pop,columns=['gbd_version','location_id','year','sex_id','age_group_id','population']).to_csv(cls.folder/'population.csv',index=False)
        pd.DataFrame({'age_name':STUDY['ages'],'weight':[1,2,3,4,5,6,7]}).to_csv(cls.folder/'weights.csv',index=False)
        cls.review={k:True for k in ['approved','pilot_verified','case_definition_verified','denominator_verified','weights_source_verified','infertility_labels_and_ids_verified','type_total_verified','raw_manifest_verified']}
        cls.review['gbd_version']='GBD 2021'
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_gate_blocks_without_review(self):
        with self.assertRaisesRegex(ValueError,'DATA GATE CLOSED'):load_validate(self.folder,{})
    def test_full_pipeline_and_additivity(self):
        out=self.folder/'output'
        self.assertEqual(run(self.folder,out,self.review),19*32*7*2*2)
        comp=pd.read_csv(out/'china_reference_comparison.csv')
        age=pd.read_csv(out/'age_contributions_and_benchmark.csv')
        cols=['year','cause_name','measure_name']
        joined=age.groupby(cols).asr_gap_contribution.sum().reset_index().merge(comp,on=cols)
        np.testing.assert_allclose(joined.asr_gap_contribution,joined.rate_difference,atol=1e-8)
        parts=pd.read_csv(out/'case_change_decomposition.csv')
        np.testing.assert_allclose(parts[['population_size','age_composition','age_specific_prevalence']].sum(axis=1),parts.net_case_change,atol=1e-6)
        self.assertEqual(len(parts),19*2*2)
    def test_bad_denominator_rejected(self):
        p=self.folder/'population.csv';original=p.read_bytes()
        try:
            x=pd.read_csv(p);x.loc[0,'population']*=2;x.to_csv(p,index=False)
            with self.assertRaisesRegex(ValueError,'does not reproduce rate'):load_validate(self.folder,self.review)
        finally:p.write_bytes(original)
    def test_wrong_outcome_and_missing_cell_rejected(self):
        p=self.folder/'burden.csv';original=p.read_bytes()
        try:
            x=pd.read_csv(p);x.loc[0,'impairment_name']='Disease total';x.to_csv(p,index=False)
            with self.assertRaisesRegex(ValueError,'infertility impairment'):load_validate(self.folder,self.review)
            pd.read_csv(p).iloc[1:].to_csv(p,index=False)
            with self.assertRaisesRegex(ValueError,'Missing or repeated'):load_validate(self.folder,self.review)
        finally:p.write_bytes(original)

if __name__=='__main__':unittest.main()
