#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 8342e4b524984d5e80168da89760799aa1a2bfba
bash /home/check_git_changes.sh

cargo test || true

