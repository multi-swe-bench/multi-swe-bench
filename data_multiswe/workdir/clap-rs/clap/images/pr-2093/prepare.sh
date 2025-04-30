#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a56a82629d1a990efb37dae9c75a76e943f22a0
bash /home/check_git_changes.sh

cargo test || true

