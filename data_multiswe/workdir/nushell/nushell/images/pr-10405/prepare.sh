#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout bc7736bc9965d2df2e406f0e4fe9f4fe0d8c29f7
bash /home/check_git_changes.sh

cargo test || true

