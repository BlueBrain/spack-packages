cd $WORKSPACE

# remove old repo if any
rm -rf spack-config spack-repo $HOME/.spack

# clone configuration repos
git clone ssh://bbpcode.epfl.ch/user/kumbhar/spack-config
git clone ssh://bbpcode.epfl.ch/user/kumbhar/spack-repo

# some spack path setup
export SPACK_ROOT=`pwd`
export PATH=$SPACK_ROOT/bin:$PATH
source $SPACK_ROOT/share/spack/setup-env.sh

# add neuron-coreneuron packages to spack
spack repo add --scope site spack-repo

# just for testing
spack arch

# arch specific directories
if [ $platform == "cscsviz" ]
then
    spack_arch_config="$HOME/.spack/linux"
    setting_arch_dir="spack-config/bbpviz"
else
    spack_arch_config="$HOME/.spack/bgq"
    setting_arch_dir="spack-config/bbpbgq"
fi

# copy arch specific setting files
mkdir -p $spack_arch_config
cp -r $setting_arch_dir/* $spack_arch_config/

# directory where packages and modules will be built
PREFIX=/gpfs/bbp.cscs.ch/scratch/gss/bgq/kumbhar/SPACK_INSTALLS/SPACK_BBP_PREFIX
TIMESTAMP=$(date +%Y_%m_%d_%H_%M)
install_prefix="$PREFIX/$platform/install/$TIMESTAMP"
module_prefix="$PREFIX/$platform/modules/$TIMESTAMP"


# make a new prefix for this build
sed -i "s#install_tree:.*#install_tree: $install_prefix #g" $spack_arch_config/config.yaml
sed -i "s#tcl:.*#tcl: $module_prefix #g" $spack_arch_config/config.yaml


# some extra options
extra_opt="--log-format=junit --dirty"


# tau profiling options
tau_selector_file="`pwd`/spack-config/nrnperfmodels.tau"
export TAU_OPTIONS="-optPDTInst -optNoCompInst -optRevert -optVerbose -optTauSelectFile=$tau_selector_file"

# the list of packages that we want to install
dev_packages=(
    'neuronperfmodels@neuron'
    'neuronperfmodels@neuron +profile'
    'coreneuron@perfmodels +mpi'
    'coreneuron@perfmodels +mpi +profile'
)


# each platform has different compilers
if [ $platform == "cscsviz" ]
then
    # compilers on the viz cluster
    compilers=(
      "pgi"
      "gcc"
      "intel"
    )

    # mpi packages associated with compilers
    declare -A mpi
    mpi["pgi"]="mpich"
    mpi["gcc"]="mvapich2"
    mpi["intel"]="intelmpi"
else
    # compilers on the viz cluster
    compilers=(
      "xl"
    )

    # mpi packages associated with compilers
    declare -A mpi
    mpi["xl"]="mpich"
fi


# for every compiler in the platform
for compiler in "${compilers[@]}"
do

    # build each package
    for package in "${dev_packages[@]}"
    do
        # spec is show just for information purpose
        spack spec $package %$compiler ^${mpi[$compiler]}

        # install package
        spack install $extra_opt $package %$compiler ^${mpi[$compiler]}
    done

    # only pgi supports gpu variant of coreneuron
    if [[ $compiler == *"pgi"* ]]; then

        # non-profile version
        spack spec coreneuron@perfmodels +mpi +gpu %$compiler ^${mpi[$compiler]}
        spack install $extra_opt coreneuron@perfmodels +mpi +gpu %$compiler ^${mpi[$compiler]}

        # profiled version
        spack spec coreneuron@perfmodels +mpi +gpu +profile %$compiler ^${mpi[$compiler]}
        spack install $extra_opt coreneuron@perfmodels +mpi +gpu +profile %$compiler ^${mpi[$compiler]}
    fi

done

# just list the packages at the end
spack find -v
