#!/bin/bash

################################ CLEANUP ################################
cd $WORKSPACE
rm -rf  $HOME/.spack spack


########################## CLONE REPOSITORIES ############################
git clone https://github.com/pramodskumbhar/spack.git -b develop
export SPACK_ROOT=`pwd`/spack
export PATH=$SPACK_ROOT/bin:$PATH
source $SPACK_ROOT/share/spack/setup-env.sh


######################### ARCH & DEFAULT COMPILERS ##########################
spack arch
spack compiler find


################################ ADD PACKAGES REPO ################################
spack repo add --scope site .


################################ SET SPACK CONFIG ################################
if [ $platform == 'cscsviz' ]
then
    mkdir -p  $SPACK_ROOT/etc/spack/defaults/linux/
    cp sysconfigs/bbpviz/packages.yaml $SPACK_ROOT/etc/spack/defaults/linux/
    cp sysconfigs/bbpviz/compilers.yaml $SPACK_ROOT/etc/spack/defaults/linux/
else
    mkdir -p  $SPACK_ROOT/etc/spack/defaults/bgq/
    cp sysconfigs/bbpbgq/packages.yaml $SPACK_ROOT/etc/spack/defaults/bgq/
    cp sysconfigs/bbpbgq/compilers.yaml $SPACK_ROOT/etc/spack/defaults/bgq/
fi

############################# START PACKAGE INSTALLATION #########################
./.install.sh $platform
