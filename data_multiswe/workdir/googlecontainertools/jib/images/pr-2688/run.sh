#!/bin/bash
set -e

cd /home/jib
./gradlew jib-maven-plugin:test --tests com.google.cloud.tools.jib.maven.MavenProjectPropertiesTest

