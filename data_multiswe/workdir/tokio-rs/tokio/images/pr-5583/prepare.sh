#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 68b02db1543880cb95ceccc39f453f8dd2223f04
bash /home/check_git_changes.sh

cargo test || true

