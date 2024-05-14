#!/bin/bash

# shellcheck disable=SC2164
cd src

echo "Openapi schema"

python manage.py spectacular --file openapi.json --validate --format openapi-json
