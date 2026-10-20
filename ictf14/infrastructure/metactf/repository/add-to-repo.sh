#!/bin/bash

set -eux

dpkg-sig -m iCTF --sign builder "$1"
reprepro --ask-passphrase -V -b "$2" includedeb trusty "$1"

