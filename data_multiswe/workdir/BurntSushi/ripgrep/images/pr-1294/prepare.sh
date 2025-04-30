#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 392682d35296bda5c0d0cccf43bae55be3d084df
bash /home/check_git_changes.sh

cargo test || true

