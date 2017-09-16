#!/bin/bash

set -e
set -x

MPI_LIB_NAME="$1"

case "$TRAVIS_OS_NAME" in
    osx)
        brew update > /dev/null
        brew install flex bison modules
        brew install gsl
        brew tap homebrew/science
        brew install lmod
        brew install python3
        brew install boost
        brew install qt

        case "$MPI_LIB_NAME" in
            mpich|mpich3)
                brew install mpich
                ;;
            openmpi)
                brew install openmpi
                ;;
            *)
                echo "ERROR: Unknown MPI Implementation: $MPI_LIB_NAME"
                exit 1
                ;;
        esac
    ;;

    linux)
        sudo apt-get update -q
        sudo apt-get install -y imagemagick \
            qtbase5-dev qtdeclarative5-dev libqt5svg5-dev \
            libqt5serialport5-dev libqt5webkit5-dev \
            libqt5xmlpatterns5-dev libqt5x11extras5-dev \
            qml-module-qtquick-controls libpoppler-glib-dev \
            libcairo2-dev libpoppler-qt5-dev librsvg2-dev \
            libtiff5-dev libavutil-dev libavformat-dev \
            libavcodec-dev libswscale-dev

        # TODO: workaround for bug in Ubuntu 14.04
        # check https://bugs.launchpad.net/ubuntu/+source/python2.7/+bug/1115466
        sudo ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

        case "$MPI_LIB_NAME" in
            mpich|mpich3)
                sudo apt-get install -y mpich libmpich-dev
                ;;
            openmpi)
                sudo apt-get install -y openmpi-bin libopenmpi-dev
                ;;
            *)
                echo "ERROR: Unknown MPI Implementation: $MPI_LIB_NAME"
                exit 1
                ;;
        esac
        ;;

    *)
        echo "Unknown Operating System: $os"
        exit 1
        ;;
esac

# print python paths in case we need for debugging
python -c "import sysconfig; print sysconfig.get_config_var('LIBDIR')"
python3 -c "import sysconfig; print (sysconfig.get_config_var('LIBDIR'))"
