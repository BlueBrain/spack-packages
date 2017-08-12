#!/bin/bash
set -x

# spack (personal fork)
git clone https://github.com/pramodskumbhar/spack.git
cd spack && git checkout upstream

echo $PATH
env

source $SPACK_ROOT/share/spack/setup-env.sh
export PATH=$SPACK_ROOT/bin:$PATH

cd ..
mkdir -p $HOME/.spack/
cp .travis.packages.yaml $HOME/.spack/packages.yaml

# add
spack repo add --scope site .

cd $WORK_DIR

spack compilers
spack spec neuron

