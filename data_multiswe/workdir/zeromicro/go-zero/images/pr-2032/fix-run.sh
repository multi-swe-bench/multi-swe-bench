#!/bin/bash
set -e

cd /home/go-zero
git apply /home/test.patch /home/fix.patch
go test -v -count=1 ./...

