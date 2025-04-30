#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 2fd26423e2304a9fdcaeac29361249c5df8ac37b
bash /home/check_git_changes.sh

cargo test || true

