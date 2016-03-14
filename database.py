#!/usr/bin/env python
from __future__ import print_function
from flask.ext.zodb import ZODB
from flask import current_app
import pandas as pd

db = ZODB()

def get_p_df(key):
    try:
        df = db['p-data'][key]
    except KeyError:
        print('probs not in db, loading...')
        df = pd.read_csv(current_app.config['PHYLO_PROB_MAT_FN'],
                         index_col=0)
        db['p-data'] = {}
        db['p-data'][key ] = df
        print('done loading.')
    return df
