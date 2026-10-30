"""Notebook helpers; all paths relative to the moved package."""
from pathlib import Path
import pandas as pd
def figure_inputs(root,source='recomputed'):
    if source not in ['recomputed','reference']:raise ValueError('Choose recomputed or reference explicitly.')
    folder=Path(root)/('results/python' if source=='recomputed' else 'reference/aggregates')
    if not (folder/'composition_sensitivities.csv').exists():
        raise FileNotFoundError('Run notebook 01, or explicitly select reference for aggregate-only learning; reference mode is not full raw-data reproduction.')
    read=lambda n:pd.read_csv(folder/(n+'.csv'))
    a=read('all_annual_benchmark_aspr');d=read('symmetric_decomposition_1990_endpoints')
    sens=read('composition_sensitivities');shifts=read('age_weighted_reference_shifts')
    ez=read('terminal_year_audit');ez=ez[(ez.cause=='Endometriosis')&(ez.subtype=='Total')]
    ec=read('endometriosis_terminal_age_type').set_index(['age_start','subtype'])
    dyn=a[(a.source=='GBD')&(a.benchmark=='dynamic')]
    return a,d,sens,shifts,ez,ec,dyn

