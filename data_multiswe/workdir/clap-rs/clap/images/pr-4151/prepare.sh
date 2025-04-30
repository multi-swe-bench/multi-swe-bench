#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout e49cdf901fdb8c658d1636471d8aa05dde939d7c
bash /home/check_git_changes.sh

cargo test || true

