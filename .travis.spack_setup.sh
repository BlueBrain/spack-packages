#!/bin/bash
set -xe

# spack (personal fork)
git clone https://github.com/pramodskumbhar/spack.git
cd spack && git checkout upstream

set +x
source $SPACK_ROOT/share/spack/setup-env.sh
set -x

# set spack packages
cd ..
mkdir -p $HOME/.spack/
cp .travis.packages.yaml $HOME/.spack/packages.yaml

# add repository of packages
spack repo add --scope site .
