#!/bin/bash

compilers=(
    '%cce@8.6.0'
    '%intel'
)

#if any inconsistent packages
spack reindex

# uninstall all packages
spack uninstall --all --yes-to-all

# stop if iany package installation fails
set -e

#export TAU_OPTIONS='-optPDTInst -optNoCompInst -optRevert -optPdtCOpts="-D_CRAYC=1" -optTauSelectFile=~/spackconfig/nrnperfmodels.tau'

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
    # mod2c is for front-end and hence need %gcc as compiler
    # and need to build for login node architecture
    spack install coreneuron +report $compiler ^mod2c %gcc arch=cray-CNL-sandybridge
done

# to install neurodamus with intel compiler we can do
# here develop version is coreneuronsetup branch
spack install neurodamus@develop %intel

# neuron built version of network models
# spack install neuronperfmodels %intel
