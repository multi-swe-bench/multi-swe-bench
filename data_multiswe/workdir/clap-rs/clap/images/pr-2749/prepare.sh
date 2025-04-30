#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout dae86f456ef26645947ac3f452a02a819adccc79
bash /home/check_git_changes.sh

cargo test || true

