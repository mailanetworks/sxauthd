#!/bin/sh
. venv/bin/activate
cd /usr/src/sxauthd/src
python setup.py bdist_egg --exclude-source-files
