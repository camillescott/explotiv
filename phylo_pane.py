#!/usr/bin/env python
from __future__ import print_function

import json
import logging
import os

from flask import Flask, Blueprint, current_app, abort, jsonify
from flask import render_template, redirect, url_for
from jinja2 import TemplateNotFound
import pandas as pd

from common import static_folder, template_folder
from database import db

views = Blueprint('phylo_pane', __name__,
                  static_folder=static_folder,
                  template_folder=template_folder)

@views.errorhandler(404)
def error_404_page(error):
    return render_template('404.html', msg=error.description), 404

@views.route('/')
def phylo_viz():
    return render_template('explotiv.html')

@views.route('/probabilities')
def probabilities():
    key = os.path.basename(current_app.config['PHYLO_PROB_FN'])
    try:
        phylo_probs = db['phylo'][key]
    except KeyError:
        print('probs not in db, loading')
        with open(current_app.config['PHYLO_PROB_FN']) as fp:
            phylo_probs = json.load(fp)
        db['phylo'] = {}
        db['phylo'][key] = phylo_probs

    return jsonify({'data': phylo_probs})
