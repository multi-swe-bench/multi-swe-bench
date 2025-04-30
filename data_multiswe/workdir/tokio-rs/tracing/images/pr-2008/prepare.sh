#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 201d21ac034f6121c4495dfa96acc18622f913e4
bash /home/check_git_changes.sh

cargo test || true

