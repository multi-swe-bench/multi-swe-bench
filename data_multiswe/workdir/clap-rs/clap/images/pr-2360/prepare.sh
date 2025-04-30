#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 30d784ffd1f9d36ed3b66ab63c44307b1166fa66
bash /home/check_git_changes.sh

cargo test || true

