#!/bin/bash

set -e

# the list of packages for linux and osx could be different

if [[ "$TRAVIS_OS_NAME" == "linux" ]]; then
    packages=(
        'mod2c'
        'coreneuron ~neurodamusmod ~report'
        'neuron@develop +python ^python@3.5.3'
        'neuron@develop +python ^python@2.7.13'
    )

    # for module support on linux
    source /etc/profile.d/modules.sh

else
    packages=(
        'mod2c'
        'coreneuron ~neurodamusmod ~report'
        'neuron@develop +python ^python@3.6.2'
        'neuron@develop +python ^python@2.7.12'
    )

    # for module support on osx
    source /usr/local/opt/modules/Modules/init/bash;
fi

# NOTE : if configure fails we have to get use something like below to print log
#        find /tmp/travis/spack-stage -name 'config.log' -exec cat {} \;

for package in "${packages[@]}"
do
    spack install -v $package

    # check if package installed properly
    if [[ `spack find $package` == *"No package matches"* ]];  then
        echo "Package Installation Check Failed For $package %$compiler !"
        exit 1
    else
        echo "-------** INSTALLED $package **-------"
    fi

done

source $SPACK_ROOT/share/spack/setup-env.sh
# show available modules
module av

# show all dependency
spack find -d

# load one of the module
spack load neuron
module list
