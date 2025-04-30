#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout c06c9952b61f35a7881b399cd21d0a4f821e7055
bash /home/check_git_changes.sh

cargo test || true

