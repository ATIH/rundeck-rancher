#!/usr/bin/env bash

GIT_ROOT="$(git rev-parse --show-toplevel)"

BUILD_DEST="${GIT_ROOT}/target"
PLUGIN_NAME='rancher-plugin'
SRC_DIR="${GIT_ROOT}/src"
SRC_NAME="$PLUGIN_NAME"
PLUGIN_ZIP="${BUILD_DEST}/${PLUGIN_NAME}.zip"

cd $SRC_DIR || { echo "Unable to reach src dir \"$SRC_DIR\"" ; exit 1 ; }

[ ! -d "$BUILD_DEST" ] && mkdir "$BUILD_DEST"

zip -r $PLUGIN_ZIP $SRC_NAME
