#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 3f933e17433cea57382b71af2f7c2a57c00ec72a
bash /home/check_git_changes.sh

cargo test || true

