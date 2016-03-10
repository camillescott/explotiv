#!/usr/bin/env python

from flask import Flask, g

from common import static_folder, template_folder
#import transcript_pane
#from database import db
import phylo_pane

DIRECTORY = None
ZODB_STORAGE = None

def run(args):
    #DIRECTORY = os.path.abspath(args.directory)
    #ZODB_STORAGE = 'file://' + os.path.join(DIRECTORY, common.CONFIG['settings']['database_filename'])

    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
    app.config.from_object(__name__)
    #app.register_blueprint(transcript_pane.views)
    app.register_blueprint(phylo_pane.views)
    #db.init_app(app)

    app.run(host=args.host, port=args.port, debug=(not args.no_debug))
