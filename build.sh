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

# Create admin user
echo "Creating admin user..."
python manage.py create_admin --username admin --password Admin@123456 --email admin@example.com
