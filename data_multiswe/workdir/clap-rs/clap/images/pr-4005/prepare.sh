#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout edc7ac359fda218f82bedbdfe519ca57b8fe155c
bash /home/check_git_changes.sh

cargo test || true

