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

#### WE WILL INSTALL PYTHON AND HDF5 ONCE
dependency_install() {
    spack install --dirty hdf5 +mpi %gcc ^mvapich2
    spack install --dirty hdf5 +mpi %intel ^intelmpi
}


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

# uninstall hdf5 : not often!
#spack uninstall -a -f -d -y hdf5

#stop on error
set -e

dependency_install

#packages without MPI dependency
spack install --dirty mod2c@develop %intel
spack install --dirty mod2c@github %intel

spack install --dirty mod2c@develop %gcc
spack install --dirty mod2c@github %gcc

spack install --dirty mod2c@develop %pgi
spack install --dirty mod2c@github %pgi

for compiler_mpi in "${compiler_with_mpi[@]}"
do
    # we dont have hdf5 compiled with PGI
    if [[ $compiler_mpi != *"pgi"* ]]; then
        spack install --dirty nrnh5@develop $compiler_mpi
        spack install --dirty neuron@hdf +mpi $compiler_mpi
    fi

    spack install --dirty neuron@develop +mpi $compiler_mpi
    spack install --dirty reportinglib $compiler_mpi

    # we dont have hdf5 compiled with PGI
    if [[ $compiler_mpi != *"pgi"* ]]; then
        spack install --dirty neurodamus@master +compile $compiler_mpi
        spack install --dirty neurodamus@develop +compile $compiler_mpi
        spack install --dirty neurodamus@hdf +compile $compiler_mpi
        spack install --dirty coreneuron@hdf +mpi +report $compiler_mpi
    fi

    spack install --dirty coreneuron@develop +mpi +report $compiler_mpi
    spack install --dirty coreneuron@github +mpi +report $compiler_mpi
done
