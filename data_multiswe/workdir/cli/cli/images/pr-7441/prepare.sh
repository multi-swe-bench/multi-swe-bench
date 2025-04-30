#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 07ed1e4e8a2adc4ee46b0108cd2d464498689842
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

