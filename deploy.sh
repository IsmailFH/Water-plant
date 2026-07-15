#!/usr/bin/env bash
set -e

cd /opt/Water-plant
source venv/bin/activate

git pull origin main
pip install -r requirements-prod.txt

python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn_water_plant.service
sudo systemctl reload nginx

echo "Deploy finished ✅"
