#!/usr/bin/env bash
set -e
cd "$HOME/Library/Rime"
# 后台跑，日志写到 bzx_service.log
nohup python3 bzx_service.py file >> bzx_service.log 2>&1 &
echo "bzx_service 已启动 (pid=$!)"
