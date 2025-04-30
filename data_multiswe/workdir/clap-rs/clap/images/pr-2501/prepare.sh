#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 750aba282f1ad4ed623ef32dfe9fb04588e6dd42
bash /home/check_git_changes.sh

cargo test || true

