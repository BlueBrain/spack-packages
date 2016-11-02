# Getting Started With Spack #

This document describes basic steps required to start development environment with Spack. The idea of Spack is to bootstrap from the existing packages provided by system which could be your personal laptop or HPC cluster. Hence, following instructions are divided into  platform `independnet` and platform `specific` settings.

## Platform Independent Settings ##

#### Prefix ####
We will use following prefix throughout the scripts. Set those according to your convenience:

```bash
export SOURCE_HOME_DIR=$HOME/workarena/software/sources
```


#### Clone Reository ####
Clone spack repository from Github. You can use [official repository](https://github.com/LLNL/spack) from LLNL but I am adding some modifications / workarounds for BG-Q and other systems like Lugano Vizcluster.

```bash
cd $SOURCE_HOME_DIR
git clone https://github.com/pramodk/spack.git
```

Developer Only

> cd spack
> git remote add llnl https://github.com/llnl/spack.git
> git remote add bitbucket git@bitbucket.org:pkumbhar/spack.git


NEURON and Blue Brain Project specific packages are maintained in private bitbucket repository (for time being). In order to build those packages with Spack, add bitbucket r as Spack repository:

```bash
cd $SOURCE_HOME_DIR/spack/var/spack/repos/
git clone https://pkumbhar@bitbucket.org/pkumbhar/spack-bbp.git bbp
spack repo add --scope site `pwd`/bbp
```

Note that you have to update / pull both repositories if there are any upstream changes.


#### Update .bashrc or .bash_profile ####
In order to access spack shell support, add following in your `.bashrc` (linux) or `.bash_profile` (OS X) : 

```bash
export SPACK_ROOT=$HOME/workarena/software/sources/spack
export PATH=$SPACK_ROOT/bin:$PATH
source $SPACK_ROOT/share/spack/setup-env.sh
```

## Platform Dependent Installation ##

Here are the instructions to get started on Mac, Linux, Lugano VizCluster and Lugano BG-Q System. Instructions for Cray system (like BlueWater and TITAN) will be added soon.

The configurations are present in `spackconfig` repository in btbucket:

```bash
https://pkumbhar@bitbucket.org/pkumbhar/spackconfig.git
```

### Mac OS X ###
We can start building packages like `CMake`, `GCC`, `LLVM` compilers, `MPI` packages like `MPICH` or `OpenMPI` with Spack on our laptop. But most of the time we don't want to build these packages from source as they take long time to build. It is goood idea to use `Homebrew` or `Macport` to install these pakages (from binary which is quicker). Note that you can skip installing packages from `Homebrew` if you want to install everything from source with Spack. But then you will end up building lots of dependent packages.

So lets start installing common packages that we need:

```bash
brew install autoconf automake libtool pkg-config cmake flex bison
```

Apart from Apple Clang, we may want to use `GNU` and `LLVM` compilers:

```bash
brew install gcc49 llvm
```

Make sure to create symlinks for gcc, g++ and fortran. This is because default gcc and g++ are actually clang compilers on OSX.

```bash
cd /usr/local/bin/
ln -s ../Cellar/gcc49/4.9.3/bin/g++-4.9 g++
ln -s ../Cellar/gcc49/4.9.3/bin/gcc-4.9 gcc
ln -s ../Cellar/gcc49/4.9.3/bin/gfortran-4.9 fortran

# for llvm
ln -s ../Cellar/llvm/3.9.0/bin/clang clang
ln -s ../Cellar/llvm/3.9.0/bin/clang++ clang++
```


For Zlib

```bash
brew tap homebrew/dupes
brew install zlib
```

We commonly need MPI library, we can install using `Homebrewa`. The `openmpi` library installed using `Homebrew` can be used with other compilers:

```
brew install openmpi
```

Spack uses `environment-module` i.e. `Modules` package to load / unload modules. You can install it using Spack or from `Homebrew` :

```bash
brew install modules
```

Now we have all required packages installed from `Homebrew`. Update `.bashrc_profile` with path for `modules` package so that Spack can use it:

```bash
MODULES_HOME=`brew --prefix modules`
source ${MODULES_HOME}/Modules/init/bash
```

If you are using parallel HDF5, install it using:

```bash
 brew install hdf5 --with-mpi
```

Lets start with Spack now!

#### Compielr Configuration ####

First step with Spack is to find compilers available on system. We can do this with following command:

``` bash
spack find compilers
```


This will find common compilers available in `$PATH` and print out the list:

``` bash
spack compiler find

==> Added 3 new compilers to /Users/kumbhar/.spack/darwin/compilers.yaml
   gcc@4.9.3 gcc@4.2.1  clang@7.3.0-apple
```

Note that new file `.spack/darwin/compilers.yaml` is created in `$HOME` which store all compiler configuration. This file look like :

``` bash
compilers:
- compiler:
   modules: []
   operating_system: elcapitan
   paths:
     cc: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang
     cxx: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++
     f77: null
     fc: null
   spec: clang@7.3.0-apple
- compiler:
   modules: []
   operating_system: elcapitan
   paths:
     cc: /usr/local/bin/gcc-4.9
     cxx: /usr/local/bin/g++-4.9
     f77: /usr/local/bin/gfortran-4.9
     fc: /usr/local/bin/gfortran-4.9
   spec: gcc@4.9.3
......
```

The `compilers.yaml` file has configuration for every compiler. Note that fortran compilers are *not* provided by `Clang` compiler and hence building any package requiring fortran compiler will fail with `Clang` (for example, `hdf5` package).

You can litst the compiler using `spack compilers` :

``` bash
spack compilers

==> Available compilers
-- gcc ----------------------------------------------------------
gcc@4.9.3 gcc@4.2.1
-- clang --------------------------------------------------------
clang@7.3.0-apple
```

And if you install new compiler, then force to re-search it using:

```bash
spack compiler find

==> Found no new compilers
```

Many time compilers are installed in non-standard directories which are not in $PATH. You can provide path searc compilers as:

```bash
spack compiler find /usr/local/Cellar/llvm/3.9.0/

==> Added 1 new compiler to /Users/kumbhar/.spack/darwin/compilers.yaml
   clang@3.9.0
```


#### Package Configuration ####

Second important step is to tell spack about `existing` packages. Spack can build most of the environment for you but we want to use packages like `MPI`, `CMake`, `autotools` etc. provided by system. This is more important on HPC facilities where package like `MPI` is provided by speromputing centre and we don't want to install it ourself from source. This is where `packages.yaml` file in `$HOME/.spack/darwin/` comes into action. The `packages.yaml` tells spack which existing packages to use, their versions, compiler preferences etc. For example, if you try to build package which need `CMake`, Spack will try to build `CMake` and all its dependencies from source. But we have previously installed `CMake` with `brew` and we can tell spack to use it using below `packages.yaml` :

```bash
packages:
   cmake:
       paths:
           cmake@system: /usr/local
       buildable: False
       version: [system]
```

In the above configuration we told Spack to use `CMake` from `/usr/local` (installed by `Homebrew`). We specified version of the package as `system` to indicate that this is provided by system. Finally `buildable: False` tells Spack to not build this package from source. So Spack will never try to build this package explicitly and if constraints are not satisfied, it give error like :

```bash
==> Error: The spec 'cmake' is configured as not buildable, and no matching external installs were found
```

When we specify dependency like `depends_on('cmake', type='build')`, Spack will match this with `system` version of the package. But many packages specify version constraints in the dependency like `depends_on('cmake@2.8.12:', type='build')`. This indicate that `CMake` version should be  `>=2.8.12`. To satisfiy this constraint we have to add extra version information in `packages.yaml` as:

```bash
   cmake:
       paths:
           cmake@system: /usr/local
           cmake@3.5.2: /usr/local
       buildable: False
       version: [system, 3.5.2]
```
Note that you dont have to keep `system` version in abive case because we have explicitly added version.


We can provide preferences for all packages in `packages.yaml`. For example, in the below configuration we specified compiler preferences for building any package. Also, we specify `mpich` as `MPI` provider.

```bash
   all:
       compiler: [gcc@4.9.3, clang@7.3.0-apple]
       providers:
           mpi: [mpich]
```

Another important aspect is `variants`. The `packages.yaml` allows us to specify `variant` preferences. This is important aspect while building packages on different platforms or by different members of the team. For example, consider the example of `HDF5` package. If you look at `HDF5` package using `spack info`, it shows different variants including `fortran` :

```bash
spack info hdf5
Package:    hdf5
Homepage:   http://www.hdfgroup.org/HDF5/
....
Variants:
   Name          Default   Description

   cxx           on        Enable C++ support
   debug         off       Builds a debug version of the library
   fortran       on        Enable Fortran support
....
```
On OS X we dont have fortran compilers with `llvm` toolchain. Hence we can disable fortran variant in `packages.yaml` as:

```bash
   hdf5:
       variants: ~fortran
```

With the above configuration we tell spack to not build fortan bindings of `HDF5` package. Now `HDF5` will be built by `Clang` compiler without any errors. Similarly we can specify version preferences. For example, latest `Boost` version takes long time to build. We need `Boost` for testing purpose and old version is sufficient for us:

```bash
   boost:
       version: [1.51.0]
```

`NEURON` has `pkg-config` dependency which can not be build with `GCC` on OS X. I expected `pkg-config@system` to be sufficient but somehow Spack complains about `invalid spec`. Hence I have to add extra specification to indicate that the `pkg-config` is available for `clang` as well as `GNU` using:

```bash
   pkg-config:
       paths:
           pkg-config@system%clang@7.3.0-apple: /usr/local
           pkg-config@system%gcc: /usr/local
       buildable: False
       version: [system]
```

##### False Paths for System Packages #####

Sometimes, the externally-installed package one wishes to use with Spack comes with the Operating System and is installed in a standard place — `/usr`, for example. Many other packages are there as well. If Spack adds it to build paths, then some packages might pick up dependencies from `/usr` than the intended Spack version.

In order to avoid this problem, it is advisable to specify a fake path in `packages.yaml`, thereby preventing Spack from adding the real path to compiler command lines. This will work becuase compilers normally search standard system paths, even if they are not on the command line. For example:

```bash
# Recommended for security reasons
   # Do not install OpenSSL as non-root user.
openssl:
       paths:
           openssl@system: /fake/path
       buildable: False
       version: [system]
```
Note that the `/usr/local` is also where `Homebrew` install binary packages. You have to be carefull if you have installed packages of different versions which might conflict. In this case you can use specific `Homebrew` paths like :

```bash
/usr/local/Cellar/gcc49/4.9.3/
```


With all system packages, `$HOME/.spack/mac/packages.yaml` looks like below:

```bash
packages:

   cmake:
       paths:
           cmake@system: /usr/local
           cmake@3.5.2: /usr/local
       buildable: False
       version: [system, 3.5.2]

   autoconf:
       paths:
           autoconf@system: /usr/local
       buildable: False
       version: [system]

   automake:
       paths:
           automake@system: /usr/local
       buildable: False
       version: [system]

   libtool:
       paths:
           libtool@system: /usr/local
       buildable: False
       version: [system]

   openssl:
       paths:
           openssl@system: /fake/path
       buildable: False
       version: [system]

   flex:
       paths:
           flex@system: /usr/local
       buildable: False
       version: [system]

   bison:
       paths:
           bison@system: /usr/local
       buildable: False
       version: [system]

   pkg-config:
       paths:
           pkg-config@system%clang@7.3.0-apple: /usr/local
           pkg-config@system%gcc: /usr/local
       buildable: False
       version: [system]

   environment-modules:
       paths:
           environment-modules@system: /usr/local/opt/modules
       buildable: False
       version: [system]

   hdf5:
       variants: ~fortran

   boost:
       version: [1.51.0]

   all:
       compiler: [gcc@4.9.3, clang@7.3.0-apple]
       providers:
           mpi: [mpich]
```

With above configuration we tell Spack to find various packages under `/usr/local` installed by `Homebrew`, specified compiler preferences and `mpich` as `MPI` library preference. Note that we have specified version `3.2` for `mpich` because some packages can request support specific `MPI` standard (1, 2, 3) support. 


#### Dependency Packages ####

In this setion we will install package that we explicitly depend on i.e. `Python`. If we try to use system provided `Python` package on OS X, I have experienced link errors. You can install `Python` using `Homebrew` but I saw that the `NEURON` build was not able to find include files. `Homebrew` install headers are in :

```bash
/usr/local/Cellar/python/2.7.12_2/Frameworks/Python.framework/Headers/
````

Better way is to install `Python` from source as:

```bash
$ spack install python
```

#### Spack in Action : Installing Packages ####

Now we have setup everything we needed to start installing our development packages!
We have added `bbp` package repository in the beginning. You can see which `package` repository we have added using :

```bash
$ spack repo list

2 package repositories.
bbp        /Users/kumbhar/workarena/software/sources/spack/var/spack/repos/bbp
builtin    /Users/kumbhar/workarena/software/sources/spack/var/spack/repos/builtin
```

Now you can list available packages using `spack list` command :

```bash
$ spack list *neuron*

==> 3 packages.
coreneuron  neuron  neuron-nmodl

$ spack list mod2c

==> 1 packages.
mod2c
```

We can see the dependencies of `mod2c` package with `spack spec`:

```bash
$ spack spec mod2c
Input spec
------------------------------
 mod2c
Normalized
------------------------------
 mod2c
     ^cmake@2.8.12:
Concretized
------------------------------
 mod2c@develop%gcc@4.9.3 arch=darwin-elcapitan-x86_64
     ^cmake@3.5.2%gcc@4.9.3~doc+ncurses+openssl~ownlibs~qt arch=darwin-elcapitan-x86_64

```

The `Concretized ` section gives final dependency list. Before actual installing package, we can use `fake` option to see how package will be installed :

```bash
spack install --fake mod2c
==> Installing mod2c
==> cmake is externally installed in /usr/local
==> Building mod2c
==> Successfully installed mod2c
 Fetch: .  Build: 1.15s.  Total: 1.15s.
[+] /Users/kumbhar/workarena/software/sources/spack/opt/spack/darwin-elcapitan-x86_64/gcc-4.9.3/mod2c-develop-3m7yiug24mfy677krgwgstsue6hmnrr4
```

As `CMake` is specified in `packages.yaml`, Spack says the package is externally installed and won't build it again.

We can install now `mod2c` as:

```bash
$ spack install mod2c
==> Installing mod2c
==> cmake is externally installed in /usr/local
==> Trying to fetch from file:///Users/kumbhar/workarena/software/sources/spack/var/spack/cache/mod2c/mod2c-develop.tar.gz
curl: (37) Couldn't open file /Users/kumbhar/workarena/software/sources/spack/var/
........
==> Trying to clone git repository:
 ssh://bbpcode.epfl.ch/sim/mod2c
Cloning into 'mod2c'...
remote: Counting objects: 124, done
....
==> No patches needed for mod2c
==> Building mod2c
==> Successfully installed mod2c
 Fetch: 4.07s.  Build: 14.35s.  Total: 18.43s.
[+] /Users/kumbhar/workarena/software/sources/spack/opt/spack/darwin-elcapitan-x86_64/gcc-4.9.3/mod2c-develop-3m7yiug24mfy677krgwgstsue6hmnrr4
```

You can use different compiler or version of the package during installation:

```bash
$ spack install mod2c %clang    #use clang
$ spack install mod2c@github %clang    #install github version using clang
```

You can find installed packages usinf `spack find` as:

```bash
$ spack find mod2c

==> 3 installed packages.
-- darwin-elcapitan-x86_64 / clang@7.3.0-apple ------------------
mod2c@github
-- darwin-elcapitan-x86_64 / gcc@4.9.3 --------------------------
mod2c@github  mod2c@develop
```

You can now install required packages one by one or write some script to install packages with different combinations. Here example of installing all stack with `Clang` and `GNU` compiler :

```bash
#!/bin/bash

set -x

#### LIST OF PACKAGES ####
dev_packages=(
   'mod2c@develop'
   'mod2c@github'
   'nrnh5'
   'neuron@develop'
   'neuron@hdf'
   'reportinglib'
   'neurodamus@master'
   'neurodamus@develop'
   'neurodamus@hdf'
   'coreneuron@develop'
   'coreneuron@github'
   'coreneuron@hdf'
)

compilers=(
   '%gcc'
   '%clang'
)

#### WE WILL INSTALL PYTHON AND HDF5 ONCE
dependency_install() {
for compiler in "${compilers[@]}"
   do
spack install python $compiler
spack install hdf5 $compiler
done
}

##### UNINSTALL PACKAGE #####
uninstall_package() {
for package in "${dev_packages[@]}"
   do
spack uninstall -a -f -d -y $package
done
}

# if any inconsistent packages
spack reindex

# uninstall packages
uninstall_package

# install dependency packages like python and hdf5
dependency_install

# stop if iany package installation fails
set -e

# for every compiler, build each package
for compiler in "${compilers[@]}"
do
for package in "${dev_packages[@]}"
   do
      spack install $package $compile
   done
done
```

##### Development using Spack #####

We saw how to install packages using Spack. If we want to develop using spack, the wokflow is as follows:

* Clone your package source repository and `cd` to the source directory:

```bash
git clone ssh://kumbhar@bbpcode.epfl.ch/sim/coreneuron
cd coreneuron
```

* Use `setup` command to create build directory:

```bash
spack setup coreneuron@develop %gcc

#on lugano vizcluster we have to explicitly specify mpi variant and dependency
 spack setup coreneuron@develop +mpi %gcc ^mvapich
```

This will create `spack-build-develop` directory and will execute `cmake`, `make` and `make install` commands. Note that if package is previously installed then `make install` will fail to copy the files to install prefix (you can ignore this). Now you can get development enviroment using `env` command:

```bash
cd spack-build-develop/
spack env coreneuron@develop %gcc -- bash

#on viz cluster
spack env coreneuron@develop +mpi %gcc ^mvapich -- bash
```

Now you can modify your code and compile using `make` and also install it using `make install`.


### Lugano Vizcluster ###

All above instructions for OS X platform will be useful to setup development environment on Lugano Vizcluster, read those first. We list few important exceptions that we must have to consider :

* On HPC cluster system like `Lugano Vizcluster`, we dont want to / should not install compilers, MPI libraries etc.
* We should use existing modules as much as possible.
* Spack discourage use of `LD_LIBRARY_PATH` from user space. Many existing modules on HPC systems set `LD_LIBRARY_PATH`. In order to use these modules, we have to use `--dirty` flag during installation (related issue has been reported upstream).
* All `MPI` packages are externally installed. The actual libraries are `mvapich`, `mpich`, `intelmpi` etc. Many times we have to specify these `MPI` libraries explicitly on command line with `install` or `spec` command like `spack spec neuron +mpi ^mvapich2` otherwise we get `list out of index` error. (this is likely a bug and has been reported upstream).
* I have used packages like `autotools`, `pkg-config` from `/usr/bin/` which is discouraged! I have seen observed that this is not causing any issues. I am using it in `packages.yaml` to quickly bootstrap without building too many packages. But it's may not be good idea!

The `$HOME/.spack/linux/packages.yaml` file for vizcluster looks like below:

```bash
packages:
   intelmpi:
       paths:
           intelmpi@6.0%intel@17.0.0 arch=linux-redhat6-x86_64: /gpfs/bbp.cscs.ch/apps/viz/intel/2017/compilers_and_libraries_2017.0.098/linux/mpi/intel64/
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
           pkg-config@0.29.1: /usr
       buildable: False
       version: [0.29.1]
   libtool:
       paths:
           libtool@system: /usr
       buildable: False
       version: [system]
   tcl:
       paths:
           tcl@8.5: /usr
       version: [8.5]
       buildable: False
   python:
       paths:
           python@system: /usr
       version: [system]
       buildable: False
   cuda:
       modules:
           cuda@6.0: cuda/6.0
       version: [6.0]
       buildable: False

   hdf5:
       variants: ~fortran
   all:
       compiler: [gcc@4.9.0, intel@17.0.0, intel@15.0.0]
       providers:
           mpi: [mvapich2, intelmpi]
           blas: [mkl]
           lapack: [mkl]
```

And build script for `Intel`, `PGI` and `GNU` compiler looks like : 

```bash

#Module issue
export LD_LIBRARY_PATH=/gpfs/bbp.cscs.ch/apps/viz/intel2017/compilers_and_libraries_2017.0.098/linux/mpi/intel64/lib/:$LD_LIBRARY_PATH


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
   '%intel ^intelmpi'
   '%gcc ^mvapich2'
)

#in case there are inconsistencies
spack reindex

uninstall_package
#spack uninstall -a -f -d -y hdf5

#stop on error
set -e

dependency_install

# hdf5 issue
spack load hdf5 +mpi %gcc ^mvapich2
spack load hdf5 +mpi %intel ^intelmpi

#packages without MPI dependency
spack install --dirty mod2c@develop %intel
spack install --dirty mod2c@github %intel

spack install --dirty mod2c@develop %gcc
spack install --dirty mod2c@github %gcc


for compiler_mpi in "${compiler_with_mpi[@]}"
do
   spack install --dirty nrnh5@develop $compiler_mpi

   spack install --dirty neuron@develop +mpi $compiler_mpi
   spack install --dirty neuron@hdf +mpi $compiler_mpi

   spack install --dirty reportinglib $compiler_mpi

   spack install --dirty neurodamus@master +compile $compiler_mpi
   spack install --dirty neurodamus@develop +compile $compiler_mpi
   spack install --dirty neurodamus@hdf +compile $compiler_mpi

   spack install --dirty coreneuron@develop +report $compiler_mpi
   spack install --dirty coreneuron@github +report $compiler_mpi
   spack install --dirty coreneuron@hdf +report $compiler_mpi
done

spack install --dirty mod2c@develop %pgi
spack install --dirty coreneuron@develop +report %pgi ^mvapich2

spack install --dirty mod2c@github %pgi
#need to push the fix to github repos
#spack install --dirty coreneuron@github +report %pgi ^mvapich2
```


## Lugano BG-Q Configuration : Incomplete / TODO ##

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
