#!/usr/bin/env python

from flask import Flask, g
import json
import os

from database import db
import database

#from dammit.common import CONFIG as dmtcfg
from common import static_folder, template_folder
#import transcript_pane
import phylo_pane


def run(args):

    database_fn = os.path.join(args.database_dir, 'explotiv.fs')
    explotiv_fn = os.path.abspath(args.input)
    database.load_explotiv_data(args.name, explotiv_fn, database_fn,
                                rewrite=args.rewrite)

    app = Flask(__name__,
                static_folder=static_folder,
                template_folder=template_folder)

    app.config['ZODB_STORAGE'] = 'file://' + database_fn
    app.config['EXPLOTIV_FN'] = explotiv_fn
    app.config['DATABASE_KEY'] = args.name

    #app.register_blueprint(transcript_pane.views)
    app.register_blueprint(phylo_pane.views)
    db.init_app(app)

    app.run(host=args.host, port=args.port, debug=(not args.no_debug))
