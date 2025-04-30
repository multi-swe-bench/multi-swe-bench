#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout a37f2908c8856dad3007e5bc8399fe89643af5a0
bash /home/check_git_changes.sh

cargo test || true

