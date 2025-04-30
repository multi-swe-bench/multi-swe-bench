#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout c4780e3305b4c2632c7d843511ae7dfe3652a569
bash /home/check_git_changes.sh

cargo test || true

