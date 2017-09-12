#!/bin/bash

#### LIST OF PACKAGES ####
dev_packages=(
    'neuronperfmodels'
    'neuronperfmodels +profile'
    'coreneuron@perfmodels +report ^reportinglib+static'
    'coreneuron@perfmodels +profile +report ^reportinglib+static'
)

compilers=(
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
uninstall_package

# stop if iany package installation fails
set -e

export TAU_OPTIONS='-optPDTInst -optNoCompInst -optRevert -optTauSelectFile=~/spackconfig/nrnperfmodels.tau'

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
	for package in "${dev_packages[@]}"
    do
        spack install -v $package $compiler
    done
done
