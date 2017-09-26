#!/bin/bash

########################################### PARSE ARGUMENTS ################################################
if [ $# -ne 1 ]; then
    echo $0: USAGE: .install.sh platform
    exit 1
fi

sysname="$1"


################################################## COMMON CHECKS ###########################################
viz_cluster=false

if [ $sysname == 'cscsviz' ];
then
    viz_cluster=true
fi

echo "SYSTEM NAME : $sysname VIZ CLUSTER : $viz_cluster"


############################################ PRE-INSTALLED PACKAGES ########################################
pre_installed_packages=('boost' 'zlib' 'cmake' 'python' 'hdf5' 'automake' 'python')
pre_installed_packages+=('libtool' 'ncurses' 'pkg-config' 'autoconf' 'm4' 'flex' 'bison')

if $viz_cluster; then
    pre_installed_packages+=('cuda' 'qt')
fi


########################################## OPTIONS FOR TAU PROFILER #######################################
export TAU_OPTIONS="-optPDTInst -optNoCompInst -optRevert -optVerbose -optTauSelectFile=`pwd`/perfconfigs/nrnperfmodels.min.tau"


############################################## GLOBAL VARIABLES ###########################################
compilers=()
packages=()
declare -A mpis


##################################### FUNCTION TO INSTALL & VERIFY PACKAGES ###############################
function install_packages {
    extra_spec="$1"

    # for each compiler
    for compiler in "${compilers[@]}"
    do
        # build each package
        for package in "${packages[@]}"
        do
            if [[ $package == *"+mpi"* ]]; then
                full_spec="$package %$compiler ^${mpis[$compiler]} $extra_spec"
            else
                full_spec="$package %$compiler $extra_spec"
            fi

            # spec is show just for information purpose
            echo " == > CHECKING SPEC : spack spec -I $full_spec "
            spack spec -I $full_spec

            # install package
            echo " == > INSTALLING PACKAGE : spack install $install_options $full_spec"
            spack install $install_options $full_spec

            # if there is no matching package then show build log
            if [[ `spack find $full_spec` == *"No package matches"* ]]; then
                echo "Package Installation Check Failed For $full_spec, Install log :"
                cat `spack location $full_spec`/spack-build.out
                exit 1
            fi
        done
    done
}


######################################## CELLULAR SIMULATION PACKAHES ####################################
gcc_package_group=(
  'neuron ~shared ~python ~mpi'
  'neuron +shared +python +mpi'
  'neurodamus@master +special'
  'coreneuron ~mpi'
  'coreneuron +mpi'
  'nest@develop +python'
  'lengine@python26 threading=omp +pybinding'
)

gcc_intel_pgi_package_group=(
  'neuronperfmodels@neuron'
  'coreneuron@perfmodels +mpi'
  'coreneuron ~neurodamus +mpi'
  'neuronperfmodels@neuron +profile'
  'coreneuron@perfmodels +profile +mpi'
)

pgi_gpu_package_group=(
  'coreneuron +gpu'
)

xl_package_group=(
  'neuronperfmodels@neuron'
  'coreneuron@perfmodels +mpi'
  'neuronperfmodels@neuron +profile'
  'coreneuron@perfmodels +profile +mpi'
)


########################################### REGISTER PACKAGES ###########################################
echo " == > INSTALLING (REGISTERING) PACKAGE $package "

if $viz_cluster; then
  compilers=('gcc')
else
  compilers=('xl')
fi

packages=( "${pre_installed_packages[@]}" )
install_packages


########################################## SPACK INSTALL OPTIONS ########################################
install_options='--dirty --log-format=junit'


############################################ REGISTER PACKAGES ###########################################
if $viz_cluster; then
    mpis['gcc']='mvapich2'
    mpis['intel']='intelmpi'
    mpis['pgi']='mpich'

    compilers=('gcc')
    packages=( "${gcc_package_group[@]}" )
    install_packages

    compilers=('gcc' 'intel' 'pgi')
    packages=( "${gcc_intel_pgi_package_group[@]}" )
    install_packages

    compilers=('pgi')
    packages=( "${pgi_gpu_package_group[@]}" )
    install_packages "^cuda@6.0"
else
    mpis['xl']='mpich'

    compilers=('xl')
    packages=( "${xl_package_group[@]}" )
    install_packages
fi


######################################### SHOW INSTALLED PACKAGES #######################################
echo "-------** LIST OF ALL INSTALLED PACKAGES **-------"
spack find -v
