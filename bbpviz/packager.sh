#!/bin/bash
#SBATCH --job-name="build"
#SBATCH --time=2:00:00
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --account=proj16
#SBATCH --exclusive

set -e

# just pretty printing
red=$'\e[1;31m'
grn=$'\e[1;32m'
yel=$'\e[1;33m'
blu=$'\e[1;34m'
mag=$'\e[1;35m'
cyn=$'\e[1;36m'
end=$'\e[0m'

# available toolchanin
compiler_with_mpi=(
    '%gcc ^mvapich2'
    '%intel ^intelmpi'
)

#TODO: mod2c doesn't depend on mpi

# bbp specific packages
bbp_packages=(
    'mod2c'
    'nrnh5'
    'neuron +mpi +hdf5'
    'reportinglib'
    'neurodamus'
    'coreneuron +report +hdf5'
)

# dependency packages
required_packages=(
    'hdf5 +mpi'
)

##### INSTALL REQUIRED PACKAGE #####
install_required_package() {
    printf "\n%s \n"  "${yel}\$${end} ${grn}INSTALLING REQUIRED PACKAGES${end}"
    for compiler_mpi in "${compiler_with_mpi[@]}"
    do
        extra_param=""
        if [[ $compiler_mpi == *"intel"* ]]; then
            extra_param="--dirty"
            module load intel/compilers_and_libraries_2017.0.098 >& /dev/null
        fi

        for package in "${required_packages[@]}"
        do
                printf "    ${blu}-> spack install $extra_param $package $compiler_mpi \n${end}"
                spack install $extra_param $package $compiler_mpi
        done


        if [[ $compiler_mpi == *"intel"* ]]; then
            module purge all
        fi

    done
}

##### INSTALL REQUIRED PACKAGE #####
uninstall_required_package() {
    printf "\n%s \n"  "${yel}\$${end} ${red}UNINSTALLING REQUIRED PACKAGES${end}"
    for package in "${required_packages[@]}"
    do
        name=`echo $package | awk '{print $1;}' `
        printf "    ${blu}-> spack uninstall -y -f -d -a %s \n${end}" $name
        spack uninstall -y -f -d $name
    done
}

export IFORTCFG=$HOME/spackconfig/bbpviz/cfg/ifort.cfg
export ICPCCFG=$HOME/spackconfig/bbpviz/cfg/icc.cfg
export ICCCFG=$HOME/spackconfig/bbpviz/cfg/icc.cfg

spack reindex

##### FIRST UNINSTALL ALL PACKAGES #####

uninstall_required_package

printf "\n%s %s\n"  "${yel}\$${end} ${red}UNINSTALLING BBP PACKAGES${end}"

for package in "${bbp_packages[@]}"
do
    #extract package name
    name=`echo $package | awk '{print $1;}' `
    printf "    -> spack uninstall -y -f -d -a %s \n" $name
    spack uninstall -y -f -d $name
done

##### START INSTALLING PACKAGES #####

spack reindex
install_required_package

printf "\n%s %s\n"  "${yel}\$${end} ${grn}INSTALLING BBP PACKAGES${end}"

for compiler_mpi in "${compiler_with_mpi[@]}"
do
    for package in "${bbp_packages[@]}"
    do
        printf "    ${blu}-> spack install $package %$compiler_mpi \n${end}"
        spack install $package $compiler_mpi
    done
done
