#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout a82bdeebe9560d22a0179ae7ff8ce3986202e24d
bash /home/check_git_changes.sh

cargo test || true

