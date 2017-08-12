#!/bin/bash
set -x

export WORK_DIR=`pwd`

# spack (personal fork)
git clone https://github.com/pramodskumbhar/spack.git
cd spack && git checkout upstream

# spack (personal packages)
git clone https://github.com/pramodskumbhar/spack-packages.git

export SPACK_ROOT=`pwd`

#setup spack variables
#echo "" >> $HOME/.bashrc
#echo "#Setup SPACK path" >> $HOME/.bashrc
export SPACK_ROOT=${SPACK_ROOT}
export PATH=$SPACK_ROOT/bin:$PATH
source $SPACK_ROOT/share/spack/setup-env.sh
source  /etc/profile.d/modules.sh

spack repo add --scope site `pwd`/spack-packages

cd $WORK_DIR

mkdir -p $HOME/.spack/
cp .travis.packages.yaml $HOME/.spack/packages.yaml

spack compilers
spack spec neuron
spack spec coreneuron

