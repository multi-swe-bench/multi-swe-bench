#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout da92a32d10fbae3b76dbb3d733a7f28d3335b664
bash /home/check_git_changes.sh

cargo test || true

