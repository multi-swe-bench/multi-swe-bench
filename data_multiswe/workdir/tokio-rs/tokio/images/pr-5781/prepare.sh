#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 38d1bcd9df6af2de436c5f898829d071f8e46988
bash /home/check_git_changes.sh

cargo test || true

