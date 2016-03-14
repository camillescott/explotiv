#!/usr/bin/env python

from flask import Flask, g
import json
import os

from database import db

#from dammit.common import CONFIG as dmtcfg
from common import static_folder, template_folder
#import transcript_pane
import phylo_pane


def run(args):

    app = Flask(__name__,
                static_folder=static_folder,
                template_folder=template_folder)

    app.config['ZODB_STORAGE'] = 'file://' + os.path.join(args.database_dir,
                                                          'explotiv.fs')
    #app.config['PHYLO_PROB_FN'] = os.path.abspath(args.input)
    app.config['PHYLO_PROB_MAT_FN'] = os.path.abspath(args.input)

    #app.register_blueprint(transcript_pane.views)
    app.register_blueprint(phylo_pane.views)
    db.init_app(app)

    app.run(host=args.host, port=args.port, debug=(not args.no_debug))
