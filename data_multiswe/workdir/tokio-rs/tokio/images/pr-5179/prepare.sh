#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 9e3fb1673a73046363af64c09a040eeed67f2a4c
bash /home/check_git_changes.sh

cargo test || true

