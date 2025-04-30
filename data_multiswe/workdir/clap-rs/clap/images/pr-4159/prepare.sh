#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 75e340a3d98105347034b49c2ac15640cbaa49cf
bash /home/check_git_changes.sh

cargo test || true

