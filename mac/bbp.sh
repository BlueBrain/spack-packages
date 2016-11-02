#!/bin/bash

set -x

#### LIST OF PACKAGES ####
dev_packages=(
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
    #'%gcc'

compilers=(
    '%clang'
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

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
	for package in "${dev_packages[@]}"
    do
        spack install $package $compiler
    done
done
