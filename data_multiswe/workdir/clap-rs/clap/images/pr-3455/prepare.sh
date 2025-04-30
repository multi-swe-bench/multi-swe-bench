#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout f9bb3de75061e31a0328e8af9db477f37913c2a1
bash /home/check_git_changes.sh

cargo test || true

