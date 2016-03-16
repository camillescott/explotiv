#!/usr/bin/env python
from __future__ import print_function

import json
import logging
import os

from flask import Flask, Blueprint, current_app, abort, jsonify, g
from flask import render_template, redirect, url_for
from jinja2 import TemplateNotFound
import pandas as pd

from common import static_folder, template_folder
import database

views = Blueprint('phylo_pane', __name__,
                  static_folder=static_folder,
                  template_folder=template_folder)

@views.before_request
def before_request():
    g.db = database.get_store()

@views.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@views.errorhandler(404)
def error_404_page(error):
    return render_template('404.html', msg=error.description), 404


@views.route('/')
def phylo_viz():
    return render_template('explotiv.html')


@views.route('/probability-means')
def node_means():
    #key = current_app.config['DATABASE_KEY']
    means = g.db['means']
    return jsonify({'data': means.to_dict()})


@views.route('/node-data/<int:taxid>')
def node_data(taxid):

    try:
        data = g.db['data'].ix[taxid]
    except KeyError as e:
        abort(404, 'No database entry for taxid={0}'.format(taxid))

    return jsonify({'data': data.to_dict()})
