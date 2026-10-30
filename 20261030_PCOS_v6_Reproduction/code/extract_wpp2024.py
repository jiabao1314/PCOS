#!/usr/bin/env python3
"""Extract CC-BY-3.0-IGO UN WPP 2024 female population midyear 5-year ages.

Original source: https://population.un.org/wpp/ ; official CSV file.
Only historical 1990-2023 country values; no modelling/interpolation.
All units and mapped identifiers verified explicitly.
"""
import argparse, hashlib, json
from pathlib import Path
import pandas as pd

ISO_TO_GBD={
'ARG':'Argentina','AUS':'Australia','BRA':'Brazil','CAN':'Canada','CHN':'China',
'FRA':'France','DEU':'Germany','IND':'India','IDN':'Indonesia','ITA':'Italy',
'JPN':'Japan','KOR':'Republic of Korea','MEX':'Mexico','RUS':'Russian Federation',
'SAU':'Saudi Arabia','ZAF':'South Africa','TUR':'Türkiye','GBR':'United Kingdom',
'USA':'United States of America'}
AGES=[f'{a}-{a+4}' for a in range(15,50,5)]
YEARS=set(range(1990,2024))
COLS=['ISO3_code','LocID','Location','LocTypeName','Time','AgeGrp','PopFemale','Variant','VarID']

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--input',required=True)
 ap.add_argument('--output',required=True)
 ap.add_argument('--manifest',required=True)
 args=ap.parse_args()
 path=Path(args.input)
 digest=hashlib.sha256(path.read_bytes()).hexdigest()
 pieces=[]
 for chunk in pd.read_csv(path,compression='gzip',usecols=lambda x:x in COLS,chunksize=100000,low_memory=False):
  # ISO identifiers rather than text names avoid UN/GBD country-name divergences.
  mask=chunk.ISO3_code.isin(ISO_TO_GBD)&chunk.Time.isin(YEARS)&chunk.AgeGrp.isin(AGES)
  pieces.append(chunk.loc[mask].copy())
 df=pd.concat(pieces,ignore_index=True)
 df['age_start']=df['AgeGrp'].str.split('-').str[0].astype('int')
 df['year']=df['Time'].astype('int')
 df['gbd_country']=df['ISO3_code'].map(ISO_TO_GBD)
 assert df.PopFemale.notna().all() and (df.PopFemale>0).all()
 # WPP source file Population by 5-year age groups and sex is thousands of persons.
 df['un_female_pop']=df['PopFemale'].astype(float)*1000.
 assert df[['gbd_country','year','age_start']].duplicated().sum()==0,'Unexpected duplicate UN cells: do not silently collapse projections/areas'
 assert len(df)==len(ISO_TO_GBD)*34*7,f'UN G20 coverage incomplete: {len(df)}'
 assert set(df.ISO3_code)==set(ISO_TO_GBD) and set(df.age_start)==set(range(15,50,5))
 # select fields in unambiguous output units
 names=['gbd_country','ISO3_code','Location','LocID','year','age_start','AgeGrp','PopFemale','un_female_pop']
 out=df[names].sort_values(['gbd_country','year','age_start']).reset_index(drop=True)
 Path(args.output).parent.mkdir(parents=True,exist_ok=True)
 out.to_csv(args.output,index=False,float_format='%.9f')
 record={'source_url':'https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_PopulationByAge5GroupSex_Medium.csv.gz',
 'source_release':'UN WPP 2024, historical mid-year 1 July 1950-2023 estimates; NOT probabilistic GBD posterior draws',
 'license':'Creative Commons Attribution 3.0 IGO',
 'full_source_filename':path.name,'full_source_bytes':path.stat().st_size,'full_source_sha256':digest,
 'subset_rows':int(len(out)),'subset_sha256':hashlib.sha256(Path(args.output).read_bytes()).hexdigest(),
 'iso_codes':sorted(ISO_TO_GBD),'country_n':len(ISO_TO_GBD),'years':[1990,2023], 'ages':AGES,
 'unit_source':'thousands','unit_output':'persons','measure':'mid-year 1 July female population',
 'note':'UN WPP 2024 population reweights country shares; GBD disease-specific age rates unchanged; do not recompute GBD burden numbers using UN denominator.'}
 Path(args.manifest).parent.mkdir(parents=True,exist_ok=True)
 Path(args.manifest).write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps({k:record[k] for k in ['source_release','full_source_sha256','subset_sha256','subset_rows','country_n']},indent=2))

if __name__=='__main__':main()
