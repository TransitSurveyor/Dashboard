import os, sys, json
import zipfile
import subprocess

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from flask import send_file

from dashboard.auth import Auth

#import fields as F


STATIC_DIR = '/fare'
mod_fare = Blueprint('fare', __name__, url_prefix='/fare')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)


@mod_fare.route('/')
def index():
    return render_template(static('index.html'))


@mod_fare.route('/reports')
@Auth.requires_auth
def reports():
    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/reports')
    reportzip = os.path.join(report_dir, 'report.zip')
    return send_file(reportzip, as_attachment=True, mimetype='application/zip')
