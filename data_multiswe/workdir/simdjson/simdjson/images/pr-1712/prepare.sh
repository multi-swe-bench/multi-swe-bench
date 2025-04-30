#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout cebe3fb299a4ea6787a11d8700a9933cc838bcfb
bash /home/check_git_changes.sh

mkdir build

