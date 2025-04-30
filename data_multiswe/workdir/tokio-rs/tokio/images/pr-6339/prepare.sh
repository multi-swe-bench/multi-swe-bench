#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 84e41d4affe2f94d892c5ab2320db6d695fca536
bash /home/check_git_changes.sh

cargo test || true

