#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout be27f41f8354bfbdf0e4eb43236759b799e7816a
bash /home/check_git_changes.sh

cargo test || true

