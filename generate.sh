#!/bin/bash
cd /home/harshit/.openclaw/workspace/ai-money-machine
python3 main.py
git add index.html posts/
git commit -m "feat: generate initial blog post and index"
git push
