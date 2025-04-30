#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout afdb68dc7175b1c6b5f4ca8f6a20b55036cb2375
bash /home/check_git_changes.sh

cargo test || true

