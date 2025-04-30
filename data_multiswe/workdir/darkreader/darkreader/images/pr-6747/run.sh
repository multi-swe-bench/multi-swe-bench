#!/bin/bash
set -e

cd /home/darkreader
npm run test:ci -- --json --outputFile=test-results-unit.json

