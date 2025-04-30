#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 43c224ff47e41628ca787d116080d69bd7030c3f
bash /home/check_git_changes.sh

cargo test || true

