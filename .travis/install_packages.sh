#!/bin/bash


# for nightly/weekly builds we can test multiple compilers and build options
if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
        packages=(
                'mod2c'
                'coreneuron ~neurodamusmod ~report'
                'coreneuron ~neurodamusmod ~report ~mpi'
                'neuron@develop +python ^python@3'
                'neuron@develop +python ^python@2.7'
                'neuron@develop -python'
                'neuron@develop +shared -mpi'
        )
# for PRs do minumum builds
else
        packages=(
                'coreneuron ~neurodamusmod ~report'
                'coreneuron ~neurodamusmod ~report ~mpi'
                'neuron@develop +shared ~mpi'
                'neuron@develop +python ^python@2.7'
        )
fi


# module support
if [ "$TRAVIS_OS_NAME" == "linux" ]; then
    source /etc/profile.d/modules.sh
else
    source /usr/local/opt/modules/Modules/init/bash
fi


# spack command line support
source $SPACK_ROOT/share/spack/setup-env.sh


# list the packages
echo " == > BUILDING ${#packages[*]} PACKAGES : "${packages[*]}""


# build all packages now
for package in "${packages[@]}"
do

    # to avoid large debug log and 4MB limit, redirect to file and delete later
    echo " == > PACKAGE SPEC : spack spec -I $package "
    spack spec -I $package

    # install package
    (spack install $package; exit 0)

    # check if package installed properly
    if [[ `spack find $package` == *"No package matches"* ]];  then

        echo " == > PACKAGE INSTALLATION CHECK FAILED, BUILD LOG : "
        cat `spack location $package`/spack-build.out
        exit 1

    fi
done


# show all generated modules
echo "-------** AUTOGENERATED MODULES **-------"
source $SPACK_ROOT/share/spack/setup-env.sh
module avail
module show coreneuron


# show all installed neuron versions with dependency
echo "-------** LIST OF ALL INSTALLED PACKAGES **-------"
spack find -d
