#!/usr/bin/env bash
#
# Quick and dirty script for first time setup of flask api
# in Minerva repo. DO NOT RUN after project is setup

set -e # bail if anything goes wrong

if [[ "$(pwd)" != "MINERVA" ]] ; then exit 1; fi

python mk_flask.py \
    -w src \
    -c config.toml \
    api

python mk_flask.py \
    -c config.toml
    artifacts