#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout dc363d0b91cd0545fbc25b651fe4b593a130247b
bash /home/check_git_changes.sh

cargo test || true

