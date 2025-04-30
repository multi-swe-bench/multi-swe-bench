#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 7df02cc828c894a619687a41a7ff961461c276d3
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

