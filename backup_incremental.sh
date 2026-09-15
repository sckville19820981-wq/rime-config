#!/bin/bash
# Rime 增量备份脚本
# 推送到用户的个人仓库 sckville19820981-wq/rime-config

TARGET_REPO="git@github.com:sckville19820981-wq/rime-config.git"
BACKUP_LOG="$HOME/.config/monsoon/rime/backup.log"

echo "Starting incremental backup..."
cd ~/Library/Rime || exit 1

# 检查是否有未提交的更改
if git diff --quiet && git diff --cached --quiet; then
  echo "No changes detected. Nothing to commit."
  exit 0
fi

# 创建临时备份仓库（避免污染原始仓库）
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 克隆用户的仓库作为备份目标
git clone --depth 1 "$TARGET_REPO" "$TEMP_DIR/rime-config" 2>/dev/null || {
  echo "✗ Failed to clone target repo. Creating new clone..."
  git clone "$TARGET_REPO" "$TEMP_DIR/rime-config" || exit 1
}

cd "$TEMP_DIR/rime-config"

# 复制配置文件（排除大型词典和临时文件）
rsync -a --delete \
  --exclude='*.dict.yaml' \
  --exclude='*.gram' \
  --exclude='build' \
  --exclude='*.log' \
  --exclude='*.err' \
  --exclude='.git' \
  ~/Library/Rime/ ./

# 添加并提交
git add -A
if git diff --cached --quiet; then
  echo "No changes to backup."
  exit 0
fi

COMMIT_MSG="backup: $(date '+%Y-%m-%d %H:%M')"
git commit -m "$COMMIT_MSG"

# 推送到 GitHub
if git push origin main; then
  echo "✓ Incremental backup pushed to GitHub"
  echo "  Repo: sckville19820981-wq/rime-config"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $COMMIT_MSG → pushed" >> "$BACKUP_LOG"
else
  echo "✗ Push failed."
  exit 1
fi
