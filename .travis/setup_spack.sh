#!/bin/bash
set -xe


# copy os specific spack configuration
cd $TRAVIS_BUILD_DIR
mkdir -p $HOME/.spack/
cp .travis/packages.$TRAVIS_OS_NAME.yaml $HOME/.spack/packages.yaml


# optional configurations for modules and naming scheme
cp .travis/modules.yaml $HOME/.spack/
cp .travis/config.yaml $HOME/.spack/


# clone spack branch (stable or develop)
cd $TRAVIS_BUILD_DIR
git clone --depth 1 https://github.com/pramodskumbhar/spack.git -b $TRAVIS_BRANCH


# setup environment
set +x
source $SPACK_ROOT/share/spack/setup-env.sh
set -x


# add repository of packages
spack repo add --scope site .


# external packages are already installed from system, this will just register to spack
spack install flex bison automake autoconf libtool pkg-config ncurses mpich openmpi python@3 python@2.7 cmake gsl
