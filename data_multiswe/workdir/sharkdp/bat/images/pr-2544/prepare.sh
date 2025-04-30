#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout c29bf2ff281f5190f90ce377eb98dac29045b6c4
bash /home/check_git_changes.sh

cargo test || true

