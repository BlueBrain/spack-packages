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
}

##### EXTRA OPTIONS FOR INSTALL #####
extra_opt="--log-format=junit --dirty"

#### WE WILL INSTALL PYTHON AND HDF5 ONCE
#dependency_install() {
#    spack install $extra_opt hdf5 +mpi %gcc ^mvapich2
#    spack install $extra_opt hdf5 +mpi %intel ^intelmpi
#}


#### COMPILER TOOLCHAINS ####
compiler_with_mpi=(
    '%pgi ^mpich'
    '%gcc ^mvapich2'
    '%intel ^intelmpi'
)

#in case there are inconsistencies
spack reindex

# uninstall all packages
uninstall_package

#stop on error
set -e

#packages without MPI dependency
spack install $extra_opt mod2c@develop %intel
spack install $extra_opt mod2c@github %intel

spack install $extra_opt mod2c@develop %gcc
spack install $extra_opt mod2c@github %gcc

spack install $extra_opt mod2c@develop %pgi
spack install $extra_opt mod2c@github %pgi

for compiler_mpi in "${compiler_with_mpi[@]}"
do
    # we dont have hdf5 compiled with PGI
    if [[ $compiler_mpi != *"pgi"* ]]; then
        spack install $extra_opt nrnh5@develop $compiler_mpi
        spack install $extra_opt neuron@hdf +mpi $compiler_mpi
    fi

    spack install $extra_opt neuron@develop +mpi $compiler_mpi
    spack install $extra_opt reportinglib $compiler_mpi

    # we dont have hdf5 compiled with PGI
    if [[ $compiler_mpi != *"pgi"* ]]; then
        spack install $extra_opt neurodamus@master +compile $compiler_mpi
        spack install $extra_opt neurodamus@develop +compile $compiler_mpi
        spack install $extra_opt neurodamus@hdf +compile $compiler_mpi
        spack install $extra_opt coreneuron@hdf +mpi +report $compiler_mpi
    fi

    spack install $extra_opt coreneuron@develop +mpi +report $compiler_mpi
    spack install $extra_opt coreneuron@github +mpi +report $compiler_mpi
done
