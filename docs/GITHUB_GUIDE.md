# GitHub Guide for Where to DINE Project

A comprehensive guide to using GitHub for this project, suitable for beginners.

---

## Table of Contents

1. [What is GitHub?](#what-is-github)
2. [Initial Setup](#initial-setup)
3. [Basic Workflow](#basic-workflow)
4. [Branching Strategy](#branching-strategy)
5. [Collaboration](#collaboration)
6. [Best Practices](#best-practices)
7. [Common Commands](#common-commands)
8. [Troubleshooting](#troubleshooting)

---

## What is GitHub?

**Git** is a version control system that tracks changes to your code.
**GitHub** is a cloud platform that hosts Git repositories and enables collaboration.

### Why Use GitHub for This Project?

- **Version Control**: Track all changes, revert mistakes
- **Collaboration**: Multiple team members can work simultaneously
- **Backup**: Your code is safely stored in the cloud
- **Portfolio**: Showcase your work to employers
- **Documentation**: README and docs are displayed beautifully

---

## Initial Setup

### 1. Install Git

**Mac:**
```bash
# Check if already installed
git --version

# If not, install via Homebrew
brew install git
```

**Windows:**
Download from https://git-scm.com/download/win

**Linux:**
```bash
sudo apt-get install git  # Ubuntu/Debian
sudo yum install git      # CentOS/RHEL
```

### 2. Configure Git

```bash
# Set your name (appears in commits)
git config --global user.name "Your Name"

# Set your email (should match GitHub email)
git config --global user.email "your.email@university.edu"

# Set default branch name to main
git config --global init.defaultBranch main

# Verify configuration
git config --list
```

### 3. Create GitHub Account

1. Go to https://github.com
2. Sign up with your university email (free benefits!)
3. Verify your email

### 4. Set Up SSH Keys (Recommended)

SSH keys allow secure authentication without passwords.

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@university.edu"

# Press Enter to accept default location
# Optionally set a passphrase

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub
# Copy the output

# Add to GitHub:
# 1. Go to GitHub.com → Settings → SSH and GPG keys
# 2. Click "New SSH key"
# 3. Paste your key and save
```

Test connection:
```bash
ssh -T git@github.com
# Should see: "Hi username! You've successfully authenticated..."
```

---

## Basic Workflow

### Initialize Repository

**Option A: Start from Scratch**
```bash
# Navigate to project folder
cd where-to-dine

# Initialize git repository
git init

# Add remote (create repo on GitHub first)
git remote add origin git@github.com:yourusername/where-to-dine.git

# Add all files
git add .

# First commit
git commit -m "Initial commit: Project structure and documentation"

# Push to GitHub
git push -u origin main
```

**Option B: Clone Existing Repository**
```bash
# Clone from GitHub
git clone git@github.com:yourusername/where-to-dine.git

# Navigate into folder
cd where-to-dine
```

### Daily Workflow

```bash
# 1. Check status (see what changed)
git status

# 2. Add changes to staging
git add .                    # Add all files
git add frontend/index.html  # Add specific file

# 3. Commit changes
git commit -m "Add hotspot visualization feature"

# 4. Push to GitHub
git push origin main

# 5. Pull latest changes (if working with team)
git pull origin main
```

---

## Branching Strategy

Branches allow parallel development without breaking main code.

### Branch Types

- **main** - Stable, working code only
- **dev** - Development branch for integration
- **feature/*** - New features (e.g., `feature/clustering`)
- **fix/*** - Bug fixes (e.g., `fix/map-loading`)

### Working with Branches

```bash
# Create and switch to new branch
git checkout -b feature/service-areas

# Make changes, commit
git add .
git commit -m "Implement service area calculation"

# Push branch to GitHub
git push origin feature/service-areas

# Switch back to main
git checkout main

# Merge feature into main
git merge feature/service-areas

# Delete branch after merging
git branch -d feature/service-areas
```

### Team Workflow Example

```bash
# Team Member 1: Works on clustering
git checkout -b feature/clustering
# ... make changes ...
git commit -m "Add HDBSCAN clustering"
git push origin feature/clustering

# Team Member 2: Works on frontend
git checkout -b feature/map-ui
# ... make changes ...
git commit -m "Create interactive map interface"
git push origin feature/map-ui

# Later: Merge both features into main
git checkout main
git merge feature/clustering
git merge feature/map-ui
```

---

## Collaboration

### Pull Requests (PRs)

Pull requests are formal requests to merge code.

**Creating a Pull Request:**

1. Push your branch to GitHub
2. Go to repository on GitHub
3. Click "Pull requests" → "New pull request"
4. Select your branch to merge into main
5. Add title and description
6. Request reviewers
7. Click "Create pull request"

**Reviewing a Pull Request:**

1. Go to "Pull requests" tab
2. Click on the PR
3. Review "Files changed" tab
4. Add comments or approve
5. Merge when approved

### Code Review Best Practices

**As Author:**
- Write clear PR description
- Keep changes focused (one feature per PR)
- Respond to feedback promptly

**As Reviewer:**
- Be constructive and respectful
- Test the changes locally
- Check for bugs, style issues
- Approve or request changes

### Resolving Merge Conflicts

Conflicts occur when two people edit the same lines.

```bash
# Pull latest changes
git pull origin main

# If conflicts occur, Git will mark them:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> branch-name

# Edit files to resolve conflicts
# Remove conflict markers
# Keep the correct code

# Mark as resolved
git add conflicted-file.js

# Complete merge
git commit -m "Resolve merge conflict in map.js"
git push origin main
```

---

## Best Practices

### Commit Messages

**Good Examples:**
```
Add clustering algorithm for restaurant data
Fix bug in service area calculation
Update README with installation instructions
Refactor map initialization code
```

**Bad Examples:**
```
Update
Fixed stuff
asdfasdf
Changes
```

**Format:**
```
<type>: <short description>

[Optional detailed description]

[Optional: Issue references]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### What to Commit

**DO Commit:**
- Source code (.py, .js, .html, .css)
- Configuration files
- Documentation
- Small test data samples

**DON'T Commit:**
- Large data files (use Git LFS or external storage)
- API keys / passwords
- Virtual environments (`venv/`, `node_modules/`)
- IDE-specific files (`.vscode/`, `.idea/`)

### Using .gitignore

Create `.gitignore` file:

```
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Data
data/raw/*.csv
data/raw/*.parquet
*.geojson

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Secrets
.env
config/secrets.json
```

---

## Common Commands

### Status & Information

```bash
git status                 # See changed files
git log                    # View commit history
git log --oneline          # Compact commit history
git diff                   # See unstaged changes
git diff --staged          # See staged changes
git branch                 # List branches
git branch -a              # List all branches (including remote)
```

### Making Changes

```bash
git add <file>             # Stage specific file
git add .                  # Stage all changes
git commit -m "message"    # Commit staged changes
git commit -am "message"   # Stage and commit (tracked files only)
git push origin main       # Push to GitHub
git pull origin main       # Pull from GitHub
```

### Branches

```bash
git branch <name>          # Create branch
git checkout <name>        # Switch to branch
git checkout -b <name>     # Create and switch
git merge <name>           # Merge branch into current
git branch -d <name>       # Delete branch
git push origin <name>     # Push branch to GitHub
```

### Undoing Changes

```bash
git checkout -- <file>     # Discard changes in file
git reset HEAD <file>      # Unstage file
git revert <commit>        # Create new commit that undoes previous
git reset --hard HEAD~1    # Delete last commit (dangerous!)
```

### Remote Management

```bash
git remote -v              # Show remote URLs
git remote add origin <url> # Add remote
git remote set-url origin <url> # Change remote URL
git fetch origin           # Download changes (don't merge)
git clone <url>            # Clone repository
```

---

## Troubleshooting

### Problem: Merge Conflicts

**Solution:**
```bash
# Pull latest
git pull origin main

# Open conflicted files
# Look for <<<<<<< markers
# Edit to keep correct code
# Remove markers

# Stage resolved files
git add .

# Complete merge
git commit -m "Resolve conflicts"
```

### Problem: Accidentally Committed Large File

**Solution:**
```bash
# Remove from tracking (keeps local file)
git rm --cached large_file.csv

# Add to .gitignore
echo "large_file.csv" >> .gitignore

# Commit
git add .gitignore
git commit -m "Remove large file from tracking"
```

### Problem: Want to Undo Last Commit

**Solution:**
```bash
# Keep changes, undo commit
git reset --soft HEAD~1

# Discard changes completely (dangerous!)
git reset --hard HEAD~1
```

### Problem: Pushed Sensitive Data

**Solution:**
1. Remove from repository immediately
2. Use `git-filter-repo` or GitHub's help
3. Rotate/change the exposed credential
4. Never commit secrets again (use environment variables)

---

## GitHub Pages (Hosting Your Web App)

Host your frontend for free on GitHub Pages!

### Setup

1. Go to repository on GitHub
2. Settings → Pages
3. Source: Select branch (usually `main`)
4. Folder: `/` or `/docs` or `/frontend`
5. Save

Your site will be live at:
`https://yourusername.github.io/where-to-dine/`

### For This Project

If using `/frontend` folder:
```bash
# Option 1: Use frontend as root
git subtree push --prefix frontend origin gh-pages

# Option 2: Move index.html to root
mv frontend/index.html .
mv frontend/css .
mv frontend/js .
```

---

## Additional Resources

### Learning Resources
- **Official Git Book:** https://git-scm.com/book
- **GitHub Learning Lab:** https://lab.github.com/
- **Interactive Tutorial:** https://learngitbranching.js.org/
- **Oh Shit, Git!:** https://ohshitgit.com/ (fixing mistakes)

### GitHub Features
- **Issues:** Track bugs and tasks
- **Projects:** Kanban boards for project management
- **Wiki:** Extended documentation
- **Actions:** CI/CD automation
- **Releases:** Version tagging

---

## Quick Reference Card

```bash
# Daily workflow
git status              # Check status
git add .               # Stage changes
git commit -m "msg"     # Commit
git push origin main    # Push to GitHub
git pull origin main    # Pull from GitHub

# Branching
git checkout -b feat    # Create feature branch
git checkout main       # Switch to main
git merge feat          # Merge feature into main

# Emergency
git stash               # Save changes temporarily
git stash pop           # Restore stashed changes
git reset --hard HEAD   # Discard all changes (careful!)
```

---

**Remember:** Commit early, commit often, and always write clear commit messages!

Happy coding and collaborating!
