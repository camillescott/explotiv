#!/usr/bin/env python
from __future__ import print_function

from flask import current_app
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

import pandas as pd
import pyprind
import sys

db = SQLAlchemy()

def load_explotiv_data(key, explotiv_fn, database_uri, rewrite=False):

    if current_app:
        raise RuntimeError('Cannot load database after app is started!')
    
    engine = create_engine(database_uri)

    df = pd.read_csv(explotiv_fn, low_memory=False)
    df[df.taxid == 'root'] = -1
    df['taxid'] = df['taxid'].astype(int)
    df = pd.melt(df, id_vars='taxid', var_name='transcript', value_name='score')

    df.to_sql(key, engine, chunksize=10000, if_exists='replace')
        

