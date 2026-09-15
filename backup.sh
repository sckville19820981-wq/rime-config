#!/bin/bash
cd ~/Library/Rime || exit 1
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi
git commit -m "backup: $(date '+%Y-%m-%d %H:%M')"
git push origin main
echo "Backed up successfully."
