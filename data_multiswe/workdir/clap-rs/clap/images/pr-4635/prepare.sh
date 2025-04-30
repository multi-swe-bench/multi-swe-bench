#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 72749a3a0958c74490b8bd78c50dbd340837c773
bash /home/check_git_changes.sh

cargo test || true

