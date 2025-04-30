#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout 86dd045554c6e73de96b6bd1fcc0f0d5a0f4054b
bash /home/check_git_changes.sh

cargo test || true

