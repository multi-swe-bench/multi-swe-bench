#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 2fe49a68a4463acc5a4129228acd852dff6a7178
bash /home/check_git_changes.sh

cargo test || true

