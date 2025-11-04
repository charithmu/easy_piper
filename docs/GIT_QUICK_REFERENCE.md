# Quick Reference: Git Repository Commands

## Initial Setup

```bash
# Initialize repo and add submodules (automated)
./init_git_repo.sh

# Or manually
git init
git submodule add https://github.com/agilexrobotics/piper_sdk.git piper_sdk
git submodule add <URL> piper_sdk_ui
git submodule update --init --recursive
git add .
git commit -m "Initial commit"
git remote add origin <YOUR_REPO_URL>
git push -u origin master
```

## Daily Git Commands

```bash
# Check status
git status
git submodule status

# Update submodules to latest
git submodule update --remote

# Commit changes
git add .
git commit -m "Your message"
git push

# Pull latest changes (including submodules)
git pull
git submodule update --init --recursive
```

## For New Users

```bash
# Clone repository with submodules
git clone --recursive <YOUR_REPO_URL>
cd easy_piper

# Install
cd piper_sdk && pip install -e . && cd ..
pip install -e .[recorder]

# Test
python3 examples/simple_example.py
```

## Submodule Tips

```bash
# Update specific submodule
git submodule update --remote piper_sdk

# Work on a submodule
cd piper_sdk
git checkout -b my-feature
# Make changes
git commit -am "My changes"
git push origin my-feature
cd ..
git add piper_sdk
git commit -m "Update piper_sdk"

# Remove a submodule
git submodule deinit piper_sdk_ui
git rm piper_sdk_ui
rm -rf .git/modules/piper_sdk_ui
```

## Common Issues

```bash
# Submodule not initialized
git submodule update --init --recursive

# Detached HEAD in submodule
cd piper_sdk
git checkout master
cd ..

# Reset submodule to committed version
git submodule update --force
```

git remote add origin https://github.com/charithmu/easy_piper.git

# Push to remote
git push -u origin master

# Push submodule references
git push --recurse-submodules=on-demand