#!/bin/bash

NEW_WORKSPACE=/gpfs/bbp.cscs.ch/scratch/gss/viz/kumbhar/JENKINS/$platform
mkdir -p $NEW_WORKSPACE
rm -rf $NEW_WORKSPACE/*

cp -r . $NEW_WORKSPACE/
export WORKSPACE=$NEW_WORKSPACE

cd $WORKSPACE


################################ SETUP BUILD ENVIRONMENT ################################
cd $WORKSPACE
mkdir -p $WORKSPACE/BUILD_HOME

# spack stores cache and configs under $HOME. In order to avoid collision with
# other user's build we change $HOME to directory under current workspace
export HOME=$WORKSPACE/BUILD_HOME
rm -rf spack $HOME/.spack


##################################### CLONE REPOSITORIES #################################
git clone https://github.com/pramodskumbhar/spack.git -b $ghprbTargetBranch
export SPACK_ROOT=`pwd`/spack
export PATH=$SPACK_ROOT/bin:$PATH
source $SPACK_ROOT/share/spack/setup-env.sh


###################################### SOME INFO #########################################
echo "TARGET BRANCH : $ghprbTargetBranch"
echo "SOURCE BRANCH : $ghprbSourceBranch"


################################# ARCH & DEFAULT COMPILERS ###############################
spack arch
spack compiler find


################################### ADD PACKAGES REPO ####################################
spack repo add --scope site .


##################################### SET SPACK CONFIG ####################################
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


################################# START PACKAGE INSTALLATION ##############################
./.install.sh $platform
