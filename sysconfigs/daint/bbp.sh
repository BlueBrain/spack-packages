#!/bin/bash

#dev_packages=(
#    'neuronperfmodels'
#    'coreneuron@perfmodels +report ^reportinglib+static'
#)

#    'neuronperfmodels +profile'
#    'coreneuron@perfmodels +profile +report ^reportinglib+static'

compilers=(
    '%cce@8.5.4'
    '%intel'
)

##### UNINSTALL PACKAGE #####
uninstall_package() {
    for package in "${dev_packages[@]}"
    do
        spack uninstall -a -f -R -y $package
    done
}

#if any inconsistent packages
spack reindex

# uninstall all packages
uninstall_package

# stop if iany package installation fails
set -e

#export TAU_OPTIONS='-optPDTInst -optNoCompInst -optRevert -optPdtCOpts="-D_CRAYC=1" -optTauSelectFile=~/spackconfig/nrnperfmodels.tau'

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
    # neuron built version of network models
    spack install neuronperfmodels

    # mod2c is for front-end and hence need %gcc as compiler
    spack install coreneuron@perfmodels +report $compiler ^mod2c %gcc
done


############# This is historical information ##################

#still doesnt work
#spack install neuron +mpi +cross-compile ^craympi ^neuron-nmodl os=SuSE11
#spack install neurodamus ^neuron+mpi+cross-compile ^craympi ^neuron-nmodl os=SuSE11
#also works
#spack install -v coreneuron%intel +hdf5 ~neurodamus +report ^mpich@7.2.2 os=CNL ^nrnh5+zlib%intel os=CNL ^mod2c%gcc os=SuSE11
