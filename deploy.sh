#!/bin/bash

# Deploy script for GitHub
# This script automatically publishes results to GitHub

set -e  # Exit on error

echo "🚀 Starting deploy script..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository!"
    echo "Run: git init"
    exit 1
fi

# Check if results.json exists
if [ ! -f "results.json" ]; then
    echo "❌ Error: results.json file not found!"
    exit 1
fi

# Git configuration (if not set)
if [ -z "$(git config user.name)" ]; then
    echo "⚠️  Git user.name not set, setting default values..."
    git config user.name "VIES Checker Bot"
    git config user.email "vieschecker@example.com"
fi

# Add all changes
echo "📁 Adding changes to git..."
git add .

# Commit with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
COMMIT_MSG="Update VIES results - $TIMESTAMP"

echo "💾 Creating commit: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || echo "ℹ️  No changes to commit"

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push origin main || git push origin master

echo "✅ Successfully published to GitHub!"
echo "🌐 Your results are available at: https://YOUR-USERNAME.github.io/urlChecker/"

# Optional: open GitHub Pages URL
if command -v open &> /dev/null; then
    echo "🔗 Opening GitHub Pages..."
    # Replace YOUR-USERNAME with actual username
    # open "https://YOUR-USERNAME.github.io/urlChecker/"
fi
