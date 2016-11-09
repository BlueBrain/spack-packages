#!/bin/bash

set -x

#### LIST OF PACKAGES ####
_dev_packages=(
    'mod2c@develop'
    'mod2c@github'

    'nrnh5'

    'neuron@develop'
    'neuron@hdf'

    'reportinglib'

    'neurodamus@hdf'
    'neurodamus@develop'
    'neurodamus@master'

    'coreneuron@develop'
    'coreneuron@github'
    'coreneuron@hdf'
    'neuronperfmodels'
    'coreneuron@perfmodels'
)


dev_packages=(
    'neuronperfmodels +profile'
    'coreneuron@perfmodels +profile +report ^reportinglib+static'
)

compilers=(
    '%clang'
    '%gcc'
)

##### UNINSTALL PACKAGE #####
uninstall_package() {
	for package in "${dev_packages[@]}"
    do
	    spack uninstall -a -f -d -y $package
	done
}

#if any inconsistent packages
spack reindex

# uninstall all packages
# uninstall_package

# stop if iany package installation fails
set -e


export TAU_OPTIONS='-optPDTInst -optNoCompInst -optRevert -optVerbose -optTauSelectFile=~/spackconfig/nrnperfmodels.tau'

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
	for package in "${dev_packages[@]}"
    do
        spack install $package $compiler
    done
done
