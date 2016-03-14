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
import database

views = Blueprint('phylo_pane', __name__,
                  static_folder=static_folder,
                  template_folder=template_folder)

@views.errorhandler(404)
def error_404_page(error):
    return render_template('404.html', msg=error.description), 404

@views.route('/')
def phylo_viz():
    return render_template('explotiv.html',
                           phylo_mat_fn=current_app.config['PHYLO_PROB_MAT_FN'])


@views.route('/probability-means')
def probability_means():
    key = os.path.basename(current_app.config['PHYLO_PROB_MAT_FN'])
    df = database.get_p_df(key)

    return jsonify({'data': df.T.mean().to_dict()})
