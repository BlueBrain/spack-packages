#!/bin/bash
#SBATCH --job-name="build"
#SBATCH --time=11:50:00
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --account=proj16
#SBATCH --exclusive

set -x
set -e

#gcc
#spack install gcc@4.9.3 %gcc

#start using gcc
#spack load gcc@4.9.3

#spack compiler find

#install mpich
#spack install mpich@3.2 %gcc@4.9.3

spack install hdf5 +mpi %gcc@4.9.3 ^mvapich2

spack uninstall -y -f -d -a neuron
spack uninstall -y -f -d -a coreneuron
spack uninstall -y -f -d -a nrnh5
spack uninstall -y -f -d -a mod2c
spack uninstall -y -f -d -a reportinglib
spack uninstall -y -f -d -a neurodamus
spack uninstall -y -f -d -a neuron-nmodl

spack reindex
spack install mod2c %gcc@4.9.3
spack install nrnh5 %gcc@4.9.3 ^mvapich2
spack install neuron +mpi +hdf5 %gcc@4.9.3 ^mvapich2
spack install reportinglib %gcc@4.9.3 ^mvapich2
spack install neurodamus %gcc@4.9.3 ^mvapich2
spack install coreneuron +report +hdf5 %gcc@4.9.3 ^mvapich2

export IFORTCFG=/gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/cf/icc.cfg
export ICPCCFG=/gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/cf/icc.cfg
export ICCCFG=/gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/cf/icc.cfg

#HDF5 execute some tests which causes libimf.so error
#module load intel/icomposer-2015.0.09
module load intel/compilers_and_libraries_2017.0.098
spack install --dirty hdf5 +mpi %intel ^intelmpi
module purge all

spack reindex
spack install mod2c  %intel
spack install nrnh5 %intel ^intelmpi
spack install neuron +mpi +hdf5 %intel ^intelmpi
spack install reportinglib %intel ^intelmpi
spack install neurodamus %intel ^intelmpi
spack install coreneuron +report +hdf5 %intel ^intelmpi

