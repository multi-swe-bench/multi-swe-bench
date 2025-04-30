#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout fb7dec0e952d0d796b98650998c44a21d6775564
bash /home/check_git_changes.sh

cargo test || true

