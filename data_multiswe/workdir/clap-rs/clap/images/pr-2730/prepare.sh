#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout f085fa64f4bb463ecbcf0b163204987e33782ec5
bash /home/check_git_changes.sh

cargo test || true

