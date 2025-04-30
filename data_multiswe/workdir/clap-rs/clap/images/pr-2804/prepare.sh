#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout edd0124af07459d0dbde75c07a733dcadfff2a47
bash /home/check_git_changes.sh

cargo test || true

