#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 28162d49cd6a407bc503b128a74883f6228189b4
bash /home/check_git_changes.sh

cargo test || true

