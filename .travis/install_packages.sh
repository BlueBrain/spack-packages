#!/bin/bash

set -e

# the list of packages for linux and osx could be different

if [[ "$TRAVIS_OS_NAME" == "linux" ]]; then
    packages=(
        'mod2c'
        'coreneuron ~neurodamusmod ~report'
        'nest'
        'neuron'
    )

    # for module support on linux
    source /etc/profile.d/modules.sh

else
    packages=(
        'mod2c'
        'coreneuron ~neurodamusmod ~report'
        'nest'
        'neuron'
    )

    # for module support on osx
    source /usr/local/opt/modules/Modules/init/bash;
fi

for package in "${packages[@]}"
do
    spack install $package

    # check if package installed properly
    if [[ `spack find $package` == *"No package matches"* ]];  then
        echo "Package Installation Check Failed For $package %$compiler !"
        exit 1
    else
        echo "-------** INSTALLED $package **-------"
    fi

done

source $SPACK_ROOT/share/spack/setup-env.sh
module av
spack load mod2c
module list
