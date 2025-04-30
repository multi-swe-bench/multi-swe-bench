#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout f9dbfa82513c346940a6255336ed8a3e0f89b5f0
bash /home/check_git_changes.sh

cargo test || true

