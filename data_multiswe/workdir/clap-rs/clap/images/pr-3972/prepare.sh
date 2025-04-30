#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout d162b846ca2bcfabe9c729d33fbfbb557e7955b9
bash /home/check_git_changes.sh

cargo test || true

