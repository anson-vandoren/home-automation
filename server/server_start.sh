#!/bin/bash
PROJ_ROOT=/usr/src/home_automation/home-automation/server
PYTHON_BIN=$PROJ_ROOT/venv/bin/python3
PIP_BIN=$PROJ_ROOT/venv/bin/pip3
$PIP_BIN install -r $PROJ_ROOT/requirements.txt
$PYTHON_BIN -m flask run