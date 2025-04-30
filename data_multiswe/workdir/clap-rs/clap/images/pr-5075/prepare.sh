#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 063b1536289f72369bcd59d61449d355aa3a1d6b
bash /home/check_git_changes.sh

cargo test || true

