#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout deb14c853740ebc82feb12a9af61c30726627622
bash /home/check_git_changes.sh

cargo test || true

