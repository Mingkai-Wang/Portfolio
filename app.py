import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

def load_projects():
    """Load projects from JSON data file"""
    try:
        with open('data/projects.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Projects data file not found")
        return {"projects": [], "categories": []}
    except json.JSONDecodeError:
        logging.error("Invalid JSON in projects data file")
        return {"projects": [], "categories": []}

def get_unique_technologies(projects):
    """Extract unique technologies from all projects"""
    technologies = set()
    for project in projects:
        technologies.update(project.get('technologies', []))
    return sorted(list(technologies))

def get_unique_categories(projects):
    """Extract unique categories from all projects"""
    categories = set()
    for project in projects:
        categories.add(project.get('category', 'Other'))
    return sorted(list(categories))

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8889, debug=True)
