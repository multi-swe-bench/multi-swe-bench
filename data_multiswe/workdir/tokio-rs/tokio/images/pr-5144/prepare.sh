#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout fe1843c0e02473564ad3adc90b2c033d7c363df1
bash /home/check_git_changes.sh

cargo test || true

