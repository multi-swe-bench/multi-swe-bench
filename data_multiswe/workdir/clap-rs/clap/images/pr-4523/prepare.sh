#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout ad4726378b2ee0320bbab5569acd8869a402e9fd
bash /home/check_git_changes.sh

cargo test || true

