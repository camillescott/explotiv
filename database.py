#!/usr/bin/env python
from __future__ import print_function

from flask.ext.zodb import ZODB
from flask.ext.zodb import Dict as zdict, BTree
from ZODB import FileStorage, DB
import transaction

from flask import current_app

import pandas as pd
import pyprind
import sys

db = ZODB()

def load_explotiv_data(key, explotiv_fn, database_fn, rewrite=False):

    if current_app:
        raise RuntimeError('Cannot load database after app is started!')

    db = DB(FileStorage.FileStorage(database_fn))
    con = db.open()
    root = con.root()
    
    if key not in root:
        root[key] = BTree()
    elif key in root and 'explotiv-data' in root[key] and not rewrite:
        print('Data already loaded and rewrite=False, skipping load.',
              file=sys.stderr)
        return

    root[key]['explotiv-data'] = BTree()

    print('Reading DataFrame for ZODB load...', file=sys.stderr)
    df = pd.read_csv(explotiv_fn, index_col=0)
    print('Done reading DataFrame!', file=sys.stderr)
    bar = pyprind.ProgBar(len(df), 
                          title='Loading explotiv data from {0}'.format(explotiv_fn))
    for taxid, row in df.iterrows():
        data = zdict()
        data['mean'] = row.mean()
        data['N'] = (row > 0).sum()
        data['scores'] = row
        root[key]['explotiv-data'][taxid] = data
        bar.update()
    
    transaction.commit()
    con.close()
        

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
