#!/bin/bash
set -e

cd /home/grpc-go
go test -v -count=1 ./...

