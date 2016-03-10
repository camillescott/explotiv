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

views = Blueprint('pyhlo_pane', __name__,
                  static_folder=static_folder,
                  template_folder=template_folder)

@views.errorhandler(404)
def error_404_page(error):
    return render_template('404.html', msg=error.description), 404

@views.route('/')
def phylo_viz():
    return render_template('explotiv.html')
