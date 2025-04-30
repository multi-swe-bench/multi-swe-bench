#!/bin/bash
set -e

cd /home/cli
git apply /home/test.patch
go test -v -count=1 ./...

