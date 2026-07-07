#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create or update superuser if configured
if [ -f create_superuser.py ]; then
    echo "Creating/updating superuser..."
    python create_superuser.py
fi
