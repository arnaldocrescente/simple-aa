#!/bin/sh

set -e
set -x

cd app

coverage run --source=app -m pytest
coverage report --show-missing
coverage html --title "${@-coverage}"
