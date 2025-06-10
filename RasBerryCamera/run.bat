#!/bin/bash

dir = $(dirname "$(realpath "$0")")
source /home/tanlihua/myenv/bin/activate
FLASK_DEBUG=1 python ${dir}/app.py
deactivate