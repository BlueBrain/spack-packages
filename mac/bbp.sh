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

    'neurodamus@master'
    'neurodamus@develop'
    'neurodamus@hdf'

    'coreneuron@develop'
    'coreneuron@github'
    'coreneuron@hdf'
)

compilers=(
    '%gcc'
    '%clang'
)


#### WE WILL INSTALL PYTHON AND HDF5 ONCE
dependency_install() {
	for compiler in "${compilers[@]}"
    do
		  spack install python $compiler
		  spack install mpich $compiler
		  spack install hdf5 $compiler
	done
}

##### UNINSTALL PACKAGE #####
uninstall_package() {
	for package in "${dev_packages[@]}"
    do
		  spack uninstall -a -f -d -y $package
	done
}

#if any inconsistent packages
spack reindex

# uninstall packages
uninstall_package

# install dependency packages like python and hdf5
dependency_install

# stop if iany package installation fails
set -e

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
	for package in "${dev_packages[@]}"
    do
        # neurodamus doesnt build with Clanf compiler
        if [[ $compiler == *"clang"* ]] && [[ $package == *"neurodamus"* ]]; then
            continue
        fi
        spack install $package $compiler
    done
done
