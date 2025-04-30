#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout ce8ebe1ccce8a07b461207ebef439c20f7522deb
bash /home/check_git_changes.sh

cargo test || true

