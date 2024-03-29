#!/usr/bin/env bash
set -e

# using workaround for https://github.com/travis-ci/travis-ci/issues/8589
/opt/python/3.6.7/bin/python -m venv atests-venv
source atests-venv/bin/activate
pip3 install $(find dist -type f -iname "rfhub2-*.whl")[postgresql]
pip3 install `cat $(find -type f -iname requirements-dev.txt) | grep robotframework-requests`