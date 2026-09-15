#!/bin/bash
# Rime 全量备份脚本

BACKUP_DIR="$HOME/Documents/Codex/backups/rime"
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
BACKUP_FILE="$BACKUP_DIR/rime-full-backup-$TIMESTAMP.tar.gz"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 执行全量备份（排除大型文件）
echo "Starting full backup..."
tar -czf "$BACKUP_FILE" \
  --exclude='*.dict.yaml' \
  --exclude='*.gram' \
  --exclude='build' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='*.err' \
  --exclude='backup*.sh' \
  -C "$HOME" Library/Rime/

# 检查备份是否成功
if [ -f "$BACKUP_FILE" ]; then
  SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
  echo "✓ Backup created: $BACKUP_FILE"
  echo "  Size: $SIZE"
  
  # 生成报告
  REPORT_FILE="$BACKUP_DIR/report-$TIMESTAMP.md"
  cat > "$REPORT_FILE" << REPORT
# Rime 输入法全量备份报告

## 备份信息
- 时间：$(date '+%Y-%m-%d %H:%M:%S')
- 文件：$BACKUP_FILE
- 大小：$SIZE

## Git 状态
\`\`\`
$(git -C ~/Library/Rime log --oneline -5 2>/dev/null || echo "无 git 历史")
\`\`\`

## 包含内容
- 配置文件 (schema, custom.yaml)
- Lua 脚本
- 皮肤和主题
- 自定义短语
- 用户数据库

## 排除内容
- 大型词典文件 (*.dict.yaml, *.gram)
- build 目录
- .git 目录
- 日志文件

REPORT
  echo "✓ Report saved: $REPORT_FILE"
else
  echo "✗ Backup failed!"
  exit 1
fi
