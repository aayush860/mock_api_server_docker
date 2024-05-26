#!/bin/bash

# Run the data seeding script
python data_seed.py

# Start the Flask application with Gunicorn
gunicorn --bind 0.0.0.0:5000 api.app:app
