#!/usr/bin/env bash

python3 -m venv atests-venv
source atests-venv/bin/activate
pip3 install $(find dist -type f -iname "rfhub2-*.whl")
