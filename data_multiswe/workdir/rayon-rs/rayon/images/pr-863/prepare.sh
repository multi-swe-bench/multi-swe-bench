#!/bin/bash
set -e

cd /home/rayon
git reset --hard
bash /home/check_git_changes.sh
git checkout ebcb09b1dc53211c6b5abdf4dc5b40e4bcd0a965
bash /home/check_git_changes.sh

cargo test || true

