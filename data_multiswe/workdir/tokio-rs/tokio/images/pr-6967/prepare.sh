#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout d4178cf34924d14fca4ecf551c97b8953376f25a
bash /home/check_git_changes.sh

cargo test || true

