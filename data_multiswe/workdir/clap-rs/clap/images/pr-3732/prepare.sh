#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 740bb39f50883b5af97b62e041618d5433220245
bash /home/check_git_changes.sh

cargo test || true

