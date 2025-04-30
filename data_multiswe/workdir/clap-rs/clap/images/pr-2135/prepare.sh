#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 49f857166fe7b2d8abf9ccf8d4d89be072fce550
bash /home/check_git_changes.sh

cargo test || true

