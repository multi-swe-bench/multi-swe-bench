#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout d7f6748887b366d2a734bb0b17aac6033f959977
bash /home/check_git_changes.sh

cargo test || true

