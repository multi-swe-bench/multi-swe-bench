#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 9962393c20f2d1521aefdcf2562bef1380b4ccbe
bash /home/check_git_changes.sh

cargo test || true

