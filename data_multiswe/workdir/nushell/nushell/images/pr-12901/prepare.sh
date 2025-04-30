#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout 580c60bb821af25f838edafd8461bb206d3419f3
bash /home/check_git_changes.sh

cargo test || true

