#!/bin/bash
# This configuration file was taken from the mpi4py and Julia project
# and then modified for spack-packages repository

set -e
set -x

MPI_IMPL="$1"
os=`uname`

case "$os" in
    Darwin)
        brew update
        sudo chown -R $(whoami) /usr/local
        which python
        python --version
        #brew ls --versions python > /dev/null || brew install python
        brew ls --versions mpich || brew install mpich
        brew ls --versions flex || brew install flex
        brew ls --versions bison || brew install bison
        brew ls --versions modules || brew install modules
        brew tap homebrew/science
        brew ls --versions lmod || brew install lmod

        ls /usr/local/bin/
        which python
        python --version

        case "$MPI_IMPL" in
            mpich|mpich3)
                brew ls --versions mpich || brew install mpich
                ;;
            openmpi)
                brew ls --versions openmpi || brew install openmpi
                ;;
            *)
                echo "ERROR: Unknown MPI Implementation: $MPI_IMPL"
                exit 1
                ;;
        esac
    ;;

    Linux)
        sudo apt-get update -q

        # TODO: for bug in Ubuntu 14.04
        # check https://bugs.launchpad.net/ubuntu/+source/python2.7/+bug/1115466
        sudo ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

        case "$MPI_IMPL" in
            mpich|mpich3)
                sudo apt-get install -y gfortran libcr0 default-jdk hwloc libmpich10 libmpich-dev
                wget -q http://de.archive.ubuntu.com/ubuntu/pool/universe/m/mpich/mpich_3.0.4-6ubuntu1_amd64.deb
                sudo dpkg -i ./mpich_3.0.4-6ubuntu1_amd64.deb
                ;;
            openmpi)
                sudo apt-get install -y gfortran
                wget --no-check-certificate https://www.open-mpi.org/software/ompi/v1.10/downloads/openmpi-1.10.2.tar.gz
                tar -zxf openmpi-1.10.2.tar.gz
                cd openmpi-1.10.2
                sh ./configure --prefix=$HOME/OpenMPI > /dev/null
                make -j > /dev/null
                 make install > /dev/null
                ;;
            *)
                echo "ERROR: Unknown MPI Implementation: $MPI_IMPL"
                exit 1
                ;;
        esac
        ;;

    *)
        echo "Unknown Operating System: $os"
        exit 1
        ;;
esac
