#!/bin/bash -e
source /home/pi/curbar/310_env/bin/activate
cd /home/pi/curbar/curbargap
export DJANGO_SETTINGS_MODULE=curbargap.settings.pro
python manage.py shell < EUMetsat.batch
