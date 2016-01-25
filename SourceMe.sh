#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

export LOCAL_PLUGIN_DIR=$DIR/ufo/.build
export LOCAL_KERNEL_DIR=$DIR/ufo/kernels
export UFO_PLUGIN_PATH=$LOCAL_PLUGIN_DIR:$UFO_PLUGIN_PATH
export UFO_KERNEL_PATH=$LOCAL_KERNEL_DIR:$UFO_KERNEL_PATH
