#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 440cee8ff5d1e239462238a39d871eb1aab166cd
bash /home/check_git_changes.sh

cargo test || true

