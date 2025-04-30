#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 50fb4ca63dc7e8fb8aa2914de5c8a5b4413f2c62
bash /home/check_git_changes.sh

cargo test || true

