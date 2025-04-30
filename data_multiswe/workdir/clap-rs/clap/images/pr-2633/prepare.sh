#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 35db529b36e384f191ac2902b8c4ccf2a655d8ab
bash /home/check_git_changes.sh

cargo test || true

