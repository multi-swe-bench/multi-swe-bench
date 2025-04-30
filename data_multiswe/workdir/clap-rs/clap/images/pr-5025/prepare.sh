#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 0d9b14fa6e9ccb09fea5d7c93477b7fca8d51bdc
bash /home/check_git_changes.sh

cargo test || true

