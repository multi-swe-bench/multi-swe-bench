#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout f9208ae4e3c2e1f7eac6de20456f42f45b9d3b8d
bash /home/check_git_changes.sh

cargo test || true

