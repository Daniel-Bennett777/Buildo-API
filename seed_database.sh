#!/bin/bash
rm db.sqlite3
rm -rf ./Buildoapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations Buildoapi
python3 manage.py migrate Buildoapi
python3 manage.py loaddata users 
python3 manage.py loaddata tokens
python3 manage.py loaddata rareusers
python3 manage.py loaddata rating
python3 manage.py loaddata status
python3 manage.py loaddata workorders
python3 manage.py loaddata review

