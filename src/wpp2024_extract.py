#!/usr/bin/env python3
"""Extract official UN WPP2024 female midyear age-group population for the G20 subset."""
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
  mask=chunk.ISO3_code.isin(ISO_TO_GBD)&chunk.Time.isin(YEARS)&chunk.AgeGrp.isin(AGES)
  pieces.append(chunk.loc[mask].copy())
 df=pd.concat(pieces,ignore_index=True)
 df['age_start']=df['AgeGrp'].str.split('-').str[0].astype(int)
 df['year']=df['Time'].astype(int)
 df['gbd_country']=df['ISO3_code'].map(ISO_TO_GBD)
 assert df.PopFemale.notna().all() and (df.PopFemale>0).all()
 df['un_female_pop']=df['PopFemale'].astype(float)*1000.0
 assert df[['gbd_country','year','age_start']].duplicated().sum()==0
 assert len(df)==len(ISO_TO_GBD)*34*7,f'UN G20 coverage incomplete: {len(df)}'
 assert set(df.ISO3_code)==set(ISO_TO_GBD) and set(df.age_start)==set(range(15,50,5))
 cols=['gbd_country','ISO3_code','Location','LocID','year','age_start','AgeGrp','PopFemale','un_female_pop']
 out=df[cols].sort_values(['gbd_country','year','age_start']).reset_index(drop=True)
 Path(args.output).parent.mkdir(parents=True,exist_ok=True)
 out.to_csv(args.output,index=False,float_format='%.9f')
 record={'source_url':'https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_PopulationByAge5GroupSex_Medium.csv.gz',
 'source_release':'UN WPP 2024 historical mid-year 1 July 1950-2023 estimates; NOT GBD posterior draws',
 'license':'CC BY 3.0 IGO',
 'source_file':path.name,'source_bytes':path.stat().st_size,'source_sha256':digest,
 'subset_rows':len(out),'subset_sha256':hashlib.sha256(Path(args.output).read_bytes()).hexdigest(),
 'country_n':19,'years':[1990,2023],'ages':AGES,'unit_source':'thousands','unit_output':'persons',
 'measure':'mid-year 1 July female population',
 'note':'WPP population alters only 18-country reference shares; GBD age-specific disease rates stay unchanged.'}
 Path(args.manifest).write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(record,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
