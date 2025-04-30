#!/bin/bash
set -e

cd /home/grpc-go
git apply /home/test.patch /home/fix.patch
go test -v -count=1 ./...

