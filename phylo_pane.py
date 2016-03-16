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
import database
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


@views.route('/probability-means')
def node_means():
    key = current_app.config['DATABASE_KEY']
    means = { taxid: data['mean'] for taxid, data in \
              db[key]['explotiv-data'].iteritems() }
    return jsonify({'data': means})


@views.route('/node-data/<int:taxid>')
def node_data(taxid):
    key = current_app.config['DATABASE_KEY']

    try:
        data = db[key]['explotiv-data'][taxid]
    except KeyError as e:
        abort(404, 'No database entry for taxid={0}'.format(taxid))
    data['scores'] = data['scores'].to_dict()
    return jsonify({'data': dict(data)})
