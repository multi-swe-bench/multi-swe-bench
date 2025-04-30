#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout d4cfceedabb908068473650410924ff2a522d5d1
bash /home/check_git_changes.sh

cargo test || true

