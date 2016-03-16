#!/usr/bin/env python
from __future__ import print_function

from flask import current_app

import pandas as pd
import pyprind
import sys

def get_store(filename=None):
    if filename is None:
        filename = current_app.config['DATABASE_FN']
    return pd.HDFStore(filename)

def load_explotiv_data(key, explotiv_fn, database_fn):


    db = get_store(filename=database_fn)

    if 'data' in db:
        print('Data already loaded')
        db.close()
        return

    print('Reading DataFrame for DB load...', file=sys.stderr)
    df = pd.read_csv(explotiv_fn)
    df[df.taxid == 'root'] = -1
    df['taxid'] = df['taxid'].astype(int)
    df.set_index('taxid', inplace=True)
    print('Done reading DataFrame!', file=sys.stderr)
    
    db['data'] = df
    db['means'] = df.mean(axis=1)
    db.close()
