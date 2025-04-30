#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 55078ffec3bba78803ff646f3933a23834789e4e
bash /home/check_git_changes.sh

cargo test || true

