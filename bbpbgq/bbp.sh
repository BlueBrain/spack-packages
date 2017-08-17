#!/bin/bash
#SBATCH --job-name="neuron-coreneuron-stack"
#SBATCH --time=4:00:00
#SBATCH --partition=exception
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --account=proj16
#SBATCH --exclusive

##### EXTRA OPTIONS FOR INSTALL #####
extra_opt="--log-format=junit"

#in case there are inconsistencies
spack reindex

# tau options
export TAU_OPTIONS='-optPDTInst -optNoCompInst -optRevert -optVerbose -optTauSelectFile=~/spackconfig/nrnperfmodels.tau'

set -x

#### LIST OF PACKAGES ####
_dev_packages=(
    'mod2c@develop os=redhat6'
    'mod2c@github os=redhat6'

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
    'neuronperfmodels'
    'neuronperfmodels +profile'
    'coreneuron@perfmodels'
    'coreneuron@perfmodels +profile'
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

# purge all build cache
spack purge -s

# stop if iany package installation fails
set -e

# for every compiler, build each package
for package in "${dev_packages[@]}"
do
    spack install $extra_opt $package $compiler
done


## ADDITIONAL PACKAGES ##

# spack install -v nest +python ^python@2.7.0
# spack install -v nest ~shared +python ^python@2.7.0
