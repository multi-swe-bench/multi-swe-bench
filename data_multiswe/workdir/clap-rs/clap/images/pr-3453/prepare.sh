#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout cb06496a0d4adbd1b328ad790777de2345da5e51
bash /home/check_git_changes.sh

cargo test || true

