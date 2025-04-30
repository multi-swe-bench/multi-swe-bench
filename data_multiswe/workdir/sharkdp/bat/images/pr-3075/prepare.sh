#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout 61c9f312c9d10103b33b7d8069401304ca938f06
bash /home/check_git_changes.sh

cargo test || true

