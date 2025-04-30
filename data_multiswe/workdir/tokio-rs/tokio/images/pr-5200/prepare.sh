#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout a66802015043a2bd94b15d17c4131bc3431c8e14
bash /home/check_git_changes.sh

cargo test || true

