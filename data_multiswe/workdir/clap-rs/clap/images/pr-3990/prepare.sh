#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 2d469511f9437b5136254bac4b69ee3ac0a23267
bash /home/check_git_changes.sh

cargo test || true

