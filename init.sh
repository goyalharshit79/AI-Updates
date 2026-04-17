#!/bin/bash
cd /home/harshit/.openclaw/workspace/ai-money-machine
git config user.name "AI Bot"
git config user.email "bot@example.com"
git branch -M main
git add .
git commit -m "Initial commit with automation script"
gh repo create ai-money-machine-blog --public --source=. --remote=origin --push
