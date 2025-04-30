#!/bin/bash
set -e

cd /home/bytes
git reset --hard
bash /home/check_git_changes.sh
git checkout 09214ba51bdace6f6cb91740cee9514fc08d55ce
bash /home/check_git_changes.sh

cargo test || true

