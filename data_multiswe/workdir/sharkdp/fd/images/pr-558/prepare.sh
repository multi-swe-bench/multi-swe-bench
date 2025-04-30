#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout e44f2f854084c1e69f334ce1a99188f8b960ed4f
bash /home/check_git_changes.sh

cargo test || true

