#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout af7802a2ed1a76ae6341513b3a002244cb2c2fe8
bash /home/check_git_changes.sh

cargo test || true

