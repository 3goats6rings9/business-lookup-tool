#!/bin/bash

# This script prepares and deploys the Business Lookup & Logistics Optimization Tool to Heroku

echo "===== Preparing for Heroku Deployment ====="

# Install Heroku CLI if not already installed
if ! command -v heroku &> /dev/null; then
    echo "Installing Heroku CLI..."
    curl https://cli-assets.heroku.com/install.sh | sh
fi

# Login to Heroku (will prompt for credentials)
echo "Please login to your Heroku account:"
heroku login

# Create a new Heroku app
echo "Creating a new Heroku app..."
heroku create business-lookup-tool

# Add PostgreSQL add-on
echo "Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
echo "Setting environment variables..."
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
echo "Please set your API keys in the Heroku dashboard or run the following commands:"
echo "heroku config:set APOLLO_API_KEY=your_apollo_api_key"
echo "heroku config:set VECTORSHIFT_API_KEY=your_vectorshift_api_key"
echo "heroku config:set GOOGLE_MAPS_API_KEY=your_google_maps_api_key"

# Deploy to Heroku
echo "Deploying to Heroku..."
git push heroku master

# Open the app in browser
echo "Opening the app in browser..."
heroku open

echo "===== Deployment Complete ====="
echo "Your Business Lookup & Logistics Optimization Tool is now available at:"
heroku info -s | grep web_url | cut -d= -f2

echo "Remember to set your API keys in the Heroku dashboard under Settings > Config Vars"
