#!/bin/bash
set -e

cd /home/grpc-go
git apply /home/test.patch
go test -v -count=1 ./...

