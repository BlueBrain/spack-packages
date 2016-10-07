# README #


##Update .bashrc
```bash

git clone git@bitbucket.org:pkumbhar/spack.git
git clone https://pkumbhar@bitbucket.org/pkumbhar/spack.git

export SPACK_ROOT=$HOME/workarena/systems/.../softwares/sources/spack
export PATH=$SPACK_ROOT/bin:$PATH
source $SPACK_ROOT/share/spack/setup-env.sh
MODULES_HOME=`spack location -i environment-modules`
source ${MODULES_HOME}/Modules/init/bash
```

```bash
cd var/spack/repos/
git clone git@bitbucket.org:pkumbhar/spack-bbp.git bap
git clone https://pkumbhar@bitbucket.org/pkumbhar/spack-bbp.git bbp
spack repo add --scope site `pwd`/bbp
spack install environment-modules
```

```bash
#start using gcc
spack load gcc@4.9.3
spack compiler find

#install mpich
#spack install mpich@3.2 %gcc@4.9.3
```

## MAC ##

From homebrew install cmake (on Sierra, CMake can't be built):
```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install cmake

#find out version and path
$ which cmake
/usr/local/bin/cmake

$ cmake --version
cmake version 3.6.2
```

Create ~/.spack/packages.yaml with below entry (change paths/version) :
```bash
packages: 
    cmake:                                                                                                           
        paths:                                                                                                          
            cmake@3.6.2: /usr/local                                                                                      
        buildable: False                                                                                                
        version: [3.6.2]
    python:                                                                                                           
        paths:                                                                                                          
            python@2.7.10%clang: /usr                                                                                                                                                                                     
        version: [2.7.10]
```

Install GCC and MPICH as:
```bash
spack install environment-modules
spack install gcc@4.9.3
spack install mpich@3.2 %gcc@4.9.3
```

Now update your .profile as:
```bash
```

### BBP Packages ###

```bash
#simulation

spack uninstall -y -f -d -a neuron  %gcc@4.9.3
spack uninstall -y -f -d -a coreneuron
spack uninstall -y -f -d -a nrnh5 ^mpich@3.2 ^hdf5
spack uninstall -y -f -d -a nrnh5 ^mpich@3.2 ^hdf5
spack uninstall -y -f -d -a nrnh5
spack uninstall -y -f -d -a mod2c
spack uninstall -y -f -d -a reportinglib

spack install mod2c %gcc@4.9.3
spack install nrnh5 %gcc@4.9.3 ^mpich@3.2
spack install reportinglib %gcc@4.9.3  ^mpich@3.2
spack install neuron +mpi +hdf5 %gcc@4.9.3 ^mpich@3.2
spack install neurodamus %gcc@4.9.3 ^mpich@3.2
spack install coreneuron +report +hdf5 %gcc@4.9.3 ^mpich@3.2

#petsc
spack -d install --keep-stage -v petsc +mpi +hdf5 %gcc@4.9.3 ^mpich@3.2 ^hdf5 ^python %clang  #installing python with gcc gives same error due to header issues, compile it with clang
```

packages.yaml is simple enough for now:
```bash
$ cat ~/.spack/packages.yaml

packages:
    cmake:
        paths:
            cmake@3.6.1 arch=darwin-elcapitan-x86_64: cmake-3.6.1-gcc-4.9.3-2xoditq
        buildable: False
```

## Lugano ##

### BBP Packages ###

#### Intel ####

```bash
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
spack install -v neuron +mpi +hdf5 %intel ^intelmpi
spack install reportinglib %intel ^intelmpi
spack install neurodamus %intel ^intelmpi
spack install coreneuron +report +hdf5 %intel ^intelmpi
```

Packages.yaml file as:

```bash
$ cat ~/.spack/packages.yaml
packages:
    intelmpi:
        paths:
            #intelmpi@5.0.1%intel@15.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/impi/5.0.1.035/intel64
            #intelmpi@4.1.1%intel@15.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/impi/4.1.1.036/intel64
            intelmpi@6.0%intel@17.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/2017/compilers_and_libraries_2017.0.098/linux/mpi/intel64/
            #intelmpi@6.0%intel@17.0.0 arch=linux-redhat6-x86_64: intel/compilers_and_libraries_2017.0.098
        buildable: False
    mkl:
        paths:
            mkl@1.0%intel@15.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/mkl
        buildable: False
    cmake:
        paths:
            cmake@3.6.1 arch=linux-redhat6-x86_64: cmake-3.6.1-gcc-4.4.7-xhpqagp
        buildable: False
    mvapich2:
        paths:
            mvapich2@2.0.1 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/tools/mvapich2/mvapich2-2.0.1-nocuda-slurm-14.03.4.2/install
        buildable: False
    autoconf:
        paths:
            autoconf@system: /usr
        buildable: False
        version: [system]
    automake:
        paths:
            automake@system: /usr
        buildable: False
        version: [system]
    pkg-config:
        paths:
            pkg-config@system: /usr
        buildable: False
        version: [system]
    libtool:
        paths:
            libtool@system: /usr
        buildable: False
        version: [system]
#    hdf5:
#        version: [1.8.16]
    all:
        compiler: [gcc, intel@17.0.0, intel@15.0.0]
        providers:
            mpi: [mvapich2, intelmpi]
            blas: [mkl]
            lapack: [mkl]
```

Compiler config as:

```bash
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /usr/lib64/ccache/gcc
      cxx: /usr/lib64/ccache/g++
      f77: /usr/bin/gfortran
      fc: /usr/bin/gfortran
    spec: gcc@4.4.7
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /gpfs/bbp.cscs.ch/apps/viz/intel/composer_xe_2015.0.090/bin/intel64/icc
      cxx: /gpfs/bbp.cscs.ch/apps/viz/intel/composer_xe_2015.0.090/bin/intel64/icpc
      f77: /gpfs/bbp.cscs.ch/apps/viz/intel/composer_xe_2015.0.090/bin/intel64/ifort
      fc: /gpfs/bbp.cscs.ch/apps/viz/intel/composer_xe_2015.0.090/bin/intel64/ifort
    spec: intel@15.0.0
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/opt/spack/linux-redhat6-x86_64/gcc-4.4.7/gcc-4.9.3-hmoqz37cd4wndmpiu3r5vckufbifl5xi/bin/gcc
      cxx: /gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/opt/spack/linux-redhat6-x86_64/gcc-4.4.7/gcc-4.9.3-hmoqz37cd4wndmpiu3r5vckufbifl5xi/bin/g++
      f77: /gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/opt/spack/linux-redhat6-x86_64/gcc-4.4.7/gcc-4.9.3-hmoqz37cd4wndmpiu3r5vckufbifl5xi/bin/gfortran
      fc: /gpfs/bbp.cscs.ch/home/kumbhar/workarena/systems/lugviz/softwares/sources/spack/opt/spack/linux-redhat6-x86_64/gcc-4.4.7/gcc-4.9.3-hmoqz37cd4wndmpiu3r5vckufbifl5xi/bin/gfortran
    spec: gcc@4.9.3
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /gpfs/bbp.cscs.ch/apps/viz/intel/2017/compilers_and_libraries_2017/linux/bin/intel64/icc
      cxx: /gpfs/bbp.cscs.ch/apps/viz/intel/2017/compilers_and_libraries_2017/linux/bin/intel64/icpc
      f77: null
      fc: null
    spec: intel@17.0.0
```


##BG-Q Configuration

```bash
$cat .spack/compilers.yaml
compilers:
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /usr/lib64/ccache/gcc
      cxx: /usr/lib64/ccache/g++
      f77: /usr/bin/gfortran
      fc: /usr/bin/gfortran
    spec: gcc@4.4.7
- compiler:
    modules: []
    operating_system: redhat6
    paths:
      cc: /opt/ibmcmp/vacpp/bg/12.1/bin/xlc_r
      cxx: /opt/ibmcmp/vacpp/bg/12.1/bin/xlc++
      f77: /opt/ibmcmp/xlf/bg/14.1/bin/xlf_r
      fc: /opt/ibmcmp/xlf/bg/14.1/bin/xlf2008
    spec: xl@12.1
- compiler:
    modules: []
    operating_system: CNK
    paths:
      cc: /usr/bin/bgxlc_r
      cxx: /usr/bin/bgxlc++
      f77: /usr/bin/bgxlf_r
      fc: /usr/bin/bgxlf2008
    spec: xl@12.1
- compiler:
    modules: []
    operating_system: CNK
    paths:
      cc: /bgsys/drivers/ppcfloor/gnu-linux/bin/powerpc64-bgq-linux-gcc
      cxx: /bgsys/drivers/ppcfloor/gnu-linux/bin/powerpc64-bgq-linux-g++
      f77: /bgsys/drivers/ppcfloor/gnu-linux/bin/powerpc64-bgq-linux-gfortran
      fc: /bgsys/drivers/ppcfloor/gnu-linux/bin/powerpc64-bgq-linux-gfortran
    spec: gcc@4.4.7
```

```bash
$cat .spack/packages.yaml
packages:
    mpich:
        paths:
            mpich@3.2%xl@12.1 arch=bgq-CNK-ppc64: /bgsys/drivers/ppcfloor/comm/
            mpich@3.2%gcc@4.4.7 arch=bgq-CNK-ppc64: /bgsys/drivers/ppcfloor/comm/
        buildable: False
    autoconf:
        paths:
            autoconf@system: /usr
        buildable: False
        version: [system]
    automake:
        paths:
            automake@system: /usr
        buildable: False
        version: [system]
    pkg-config:
        paths:
            pkg-config@system: /usr
        buildable: False
        version: [system]
    cmake:
        paths:
            cmake@2.8.12: /gpfs/bbp.cscs.ch/apps/bgq/tools/cmake/cmake-2.8.12/install
        buildable: False
        version: [2.8.12]
    libtool:
        paths:
            libtool@system: /usr
        buildable: False
        version: [system]

    all:
        compiler: [xl,gcc]
        providers:
            mpi: [mpich]
```

### Installation
```bash
set -e
set -x

spack uninstall -f -a -d -y mod2c
spack uninstall -f -a -d -y nrnh5
spack uninstall -f -a -d -y neuron
spack uninstall -f -a -d -y reportinglib
spack uninstall -f -a -d -y coreneuron
spack uninstall -f -a -d -y neurodamus
spack uninstall -f -a -d -y neuron-nmodl

spack install mod2c os=redhat6
spack install reportinglib ^bgqmpi
spack install nrnh5 +zlib ^bgqmpi

spack install neuron +mpi +cross-compile ^bgqmpi ^neuron-nmodl os=redhat6
spack install neurodamus ^neuron+mpi+cross-compile ^bgqmpi ^neuron-nmodl os=redhat6
spack install coreneuron +hdf5 +neurodamus +report ^bgqmpi ^mod2c os=redhat6 ^neurodamus ^neuron+mpi+cross-compile ^neuron-nmodl os=redhat6 ^nrnh5+zlib
```

Note that the dependency of neuron for neurodamus is copied by checking spec of previous installation of neuron. And same for neuron-nmodl. For example:
```bash

spack spec neurodamus%xl os=CNK ^bgqmpi ^neuron@develop%xl@12.1~hdf5+mpi+python+with-nmodlonly arch=bgq-CNK-ppc64 ^neuron-nmodl%gcc os=redhat6
.........
Concretized
------------------------------
  neurodamus@develop%xl@12.1 arch=bgq-CNK-ppc64
        ^bgqmpi@3.2%xl@12.1 arch=bgq-CNK-ppc64
              ^hdf5@1.8.15%xl@12.1+cxx~debug+fortran+mpi+shared~szip~threadsafe arch=bgq-CNK-ppc64
                    ^neuron@develop%xl@12.1~hdf5+mpi+python+with-nmodlonly arch=bgq-CNK-ppc64
```
Use above concretized for coreneuron. but again neurodamus depend on:
```bash
.....
^neuron@develop%xl@12.1~hdf5+mpi+python+with-nmodlonly arch=bgq-CNK-ppc64 ^neuron-nmodl%gcc os=redhat6
```
So have to add those! Better way is to add variant preferences in packages.yaml file!