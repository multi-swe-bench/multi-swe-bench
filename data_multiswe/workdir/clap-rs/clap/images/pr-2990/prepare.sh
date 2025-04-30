#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 879dd23963f6ed968535d6ed7bc6f192f02a0a16
bash /home/check_git_changes.sh

cargo test || true

