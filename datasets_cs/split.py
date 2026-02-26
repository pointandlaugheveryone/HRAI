import pandas as pd


origin = pd.read_csv('/home/ronji/Dev/CarP/tabiya/data/combinedOccupations_cs.csv')

def denull(row):
    if row['ALTLABEL']=='':
        row['ALTLABEL'] = row['PREFERREDLABEL']
    return row

split_titles = origin.copy()
split_titles['ALTLABEL'] = (
    split_titles['ALTLABELS']
        .fillna('')
        .str.split('\n')
)
split_titles = split_titles.explode('ALTLABEL')
split_titles['ALTLABEL'] = split_titles['ALTLABEL'].str.strip()
split_titles = split_titles.apply(denull,axis=1)
split_titles.to_csv('combinedOccupations_augmented_cs.csv')