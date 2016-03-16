#!/usr/bin/env python

from flask import Flask, g
import json
import os
import sys

import database
from database import db

#from dammit.common import CONFIG as dmtcfg
from common import static_folder, template_folder
#import transcript_pane
import phylo_pane


def run(args):

    database_uri = 'sqlite:///' + os.path.join(args.database_dir, 'explotiv.db')
    explotiv_fn = os.path.abspath(args.input)
    database.load_explotiv_data(args.name, explotiv_fn, database_uri,
                                rewrite=args.rewrite)

    sys.exit(0)
    app = Flask(__name__,
                static_folder=static_folder,
                template_folder=template_folder)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['EXPLOTIV_FN'] = explotiv_fn
    app.config['DATABASE_KEY'] = args.name
    db.init_app(app)


    #app.register_blueprint(transcript_pane.views)
    app.register_blueprint(phylo_pane.views)

    app.run(host=args.host, port=args.port, debug=(not args.no_debug))
