#!/bin/bash

# Setup script for VIES API Checker
# Initializes git repository and sets basic configuration

echo "🔧 Setting up VIES API Checker..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git and try again."
    exit 1
fi

# Initialize git repository (if it doesn't exist)
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "ℹ️  Git repository already exists"
fi

# Set git configuration (if not set)
if [ -z "$(git config user.name)" ]; then
    echo "👤 Setting up git user..."
    read -p "Enter your name: " username
    read -p "Enter your email: " email
    
    git config user.name "$username"
    git config user.email "$email"
    echo "✅ Git configuration set"
else
    echo "ℹ️  Git configuration already exists"
fi

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# OS
.DS_Store
Thumbs.db
EOF

echo "✅ .gitignore created"

# First commit
echo "💾 Creating first commit..."
git add .
git commit -m "Initial commit - VIES API Checker setup"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Create repository on GitHub.com"
echo "2. Add remote origin:"
echo "   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git"
echo "3. Push code:"
echo "   git push -u origin main"
echo "4. Run monitoring:"
echo "   python checker.py"
echo ""
echo "💡 For automatic execution add to crontab:"
echo "   crontab -e"
echo "   # Add line: */1 * * * * cd $(pwd) && python checker.py"
