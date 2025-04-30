#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout ee2396b57a2590a9e534e407d45fa454b32df799
bash /home/check_git_changes.sh

cargo test || true

