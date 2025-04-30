#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 35158257c6e79d908723f1a7023362a718579c4f
bash /home/check_git_changes.sh

mkdir build

