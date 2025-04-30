#!/bin/bash
set -e

cd /home/go-zero
git apply /home/test.patch
go test -v -count=1 ./...

