#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 1dd3fcb954355198193a793d2983db383829ec2f
bash /home/check_git_changes.sh

cargo test || true

