#!/bin/bash
#SBATCH --job-name="neuron-coreneuron-stack"
#SBATCH --time=4:00:00
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --account=proj16
#SBATCH --exclusive

##### UNINSTALL PACKAGE #####
uninstall_package() {
    spack uninstall -y -f -d -a neuron
    spack uninstall -y -f -d -a coreneuron
    spack uninstall -y -f -d -a mod2c
    spack uninstall -y -f -d -a nrnh5
    spack uninstall -y -f -d -a reportinglib
    spack uninstall -y -f -d -a neurodamus
    spack uninstall -y -f -d -a neuron-nmodl
    spack uninstall -y -f -d -a neuronperfmodels
}

##### EXTRA OPTIONS FOR INSTALL #####
extra_opt="--log-format=junit --dirty"

#### WE WILL INSTALL PYTHON AND HDF5 ONCE
#dependency_install() {
#    spack install $extra_opt hdf5 +mpi %gcc ^mvapich2
#    spack install $extra_opt hdf5 +mpi %intel ^intelmpi
#}


#### COMPILER TOOLCHAINS ####
compilers=(
    "pgi"
    "gcc"
    "intel"
)

declare -A mpi

mpi["pgi"]="mpich"
mpi["gcc"]="mvapich2"
mpi["intel"]="intelmpi"

#in case there are inconsistencies
spack reindex

# uninstall all packages
uninstall_package

#stop on error
set -e

for compiler in "${compilers[@]}"
do
    # remove previous stages/downloads from different compilers
    spack purge -s -d

    spack install $extra_opt mod2c@develop %$compiler
    spack install $extra_opt mod2c@github  %$compiler

    # we dont have hdf5 compiled with PGI
    if [[ $compiler != *"pgi"* ]]; then
        spack install $extra_opt nrnh5@develop %$compiler ^${mpi[$compiler]}
        spack install $extra_opt neuron@hdf +mpi %$compiler ^${mpi[$compiler]}
    fi

    spack install $extra_opt neuron@develop +mpi %$compiler ^${mpi[$compiler]}
    spack install $extra_opt reportinglib %$compiler ^${mpi[$compiler]}

    # we dont have hdf5 compiled with PGI
    if [[ $compiler != *"pgi"* ]]; then
        spack install $extra_opt neurodamus@master +compile %$compiler ^${mpi[$compiler]}
        spack install $extra_opt neurodamus@develop +compile %$compiler ^${mpi[$compiler]}
        spack install $extra_opt neurodamus@hdf +compile %$compiler ^${mpi[$compiler]}
        spack install $extra_opt coreneuron@hdf +mpi +report %$compiler ^${mpi[$compiler]}
    fi

    spack install $extra_opt coreneuron@develop +mpi +report %$compiler ^${mpi[$compiler]}
    spack install $extra_opt coreneuron@github +mpi +report %$compiler ^${mpi[$compiler]}
    spack install $extra_opt neuronperfmodels@neuron %$compiler ^${mpi[$compiler]}
    spack install $extra_opt coreneuron@perfmodels +mpi +report %$compiler ^${mpi[$compiler]}
done
