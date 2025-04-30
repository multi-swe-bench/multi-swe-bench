#!/bin/bash
set -e

cd /home/jib
git apply /home/test.patch /home/fix.patch
./gradlew jib-maven-plugin:test --tests com.google.cloud.tools.jib.maven.MavenProjectPropertiesTest

