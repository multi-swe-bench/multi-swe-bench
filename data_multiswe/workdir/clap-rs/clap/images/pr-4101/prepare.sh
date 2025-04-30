#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout c023db3a98d1de3ca7067f92f31ba8109d954b99
bash /home/check_git_changes.sh

cargo test || true

