#!/bin/bash
set -e
rm app/db||true
python app/manage.py syncdb --noinput
python app/manage.py loaddata devel
PORT=$(python app/settings_selenium_tests.py)
python app/manage.py runserver 127.0.0.1:$PORT &
sleep 5
