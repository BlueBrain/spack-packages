#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
import os


class Coreneuron(Package):

    """CoreNEURON is a simplified engine for the NEURON simulator
    optimised for both memory usage and computational speed. Its goal
    is to simulate massive cell networks with minimal memory footprint
    and optimal performance."""

    homepage = "https://github.com/BlueBrain/CoreNeuron"
    url      = "https://github.com/BlueBrain/CoreNeuron"
    bbpurl   = "ssh://bbpcode.epfl.ch/sim/coreneuron"

    version('develop', git=url, preferred=True)

    # TODO: same as develop but for legacy reasons
    version('perfmodels', git=url)
    version('checkpoint', git=url, branch='checkpoint-restart_prototype')

    # development version from bbp
    version('hdf', git=bbpurl, branch='sandbox/kumbhar/nrnh5')
    version('devopt', git=bbpurl, branch='sandbox/kumbhar/dev')

    variant('mpi',           default=True,  description="Enable MPI support")
    variant('openmp',        default=True,  description="Enable OpenMP support")
    variant('neurodamusmod', default=True,  description="Build only MOD files from Neurodamus")
    variant('report',        default=True,  description="Enable reports using ReportingLib")
    variant('gpu',           default=False, description="Enable GPU build")
    variant('knl',           default=False, description="Enable KNL specific flags")
    variant('tests',         default=False, description="Enable building tests")
    variant('profile',       default=False, description="Enable profiling using Tau")

    # mandatory dependencies
    depends_on('cmake@2.8.12:', type='build')
    depends_on('mod2c', type='build')
    depends_on('mpi', when='+mpi')
    depends_on('reportinglib', when='+report')
    depends_on('cuda', when='+gpu')
    depends_on('boost', when='+tests')

    depends_on('mod2c@devopt', type='build', when='@devopt')
    depends_on('nrnh5', when='@hdf')
    depends_on('hdf5', when='@hdf')
    depends_on('zlib', when='@hdf')

    depends_on('mod2c@checkpoint', type='build', when='@checkpoint')

    # granular dependency selection for neurodamus
    depends_on('neurodamus@develop~compile', when='+neurodamusmod~gpu')
    depends_on('neurodamus@gpu~compile', when='+gpu')

    # neuron models for benchmarking
    depends_on('neuronperfmodels@coreneuron', when='@perfmodels')

    # granular dependency selection for profiling
    depends_on('tau', when='+profile')
    depends_on('reportinglib+profile', when='+report+profile')

    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def get_opt_flags(self):
        flags = "-g -O2"

        if 'bgq' in self.spec.architecture and '%xl' in self.spec:
            flags = '-O3 -qtune=qp -qarch=qp -q64 -qhot=simd -qsmp -qthreaded -g'

        if self.spec.satisfies('+knl') and '%intel' in self.spec:
            flags = '-g -xmic-avx512 -O3 -qopt-report=5'

        return flags

    def install(self, spec, prefix):

        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):

            c_compiler = spack_cc
            cxx_compiler = spack_cxx

            optflag = self.get_opt_flags()

            if spec.satisfies('+profile'):
                c_compiler = 'tau_cc'
                cxx_compiler = 'tau_cxx'
            elif 'bgq' in self.spec.architecture and spec.satisfies('+mpi'):
                # for bg-q, our cmake is not setup properly
                c_compiler = spec['mpi'].mpicc
                cxx_compiler = spec['mpi'].mpicxx

            options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                       '-DCOMPILE_LIBRARY_TYPE=STATIC',
                       '-DCMAKE_C_FLAGS=%s' % optflag,
                       '-DCMAKE_CXX_FLAGS=%s' % optflag,
                       '-DCMAKE_BUILD_TYPE=CUSTOM',
                       '-DCMAKE_C_COMPILER=%s' % c_compiler,
                       '-DCMAKE_CXX_COMPILER=%s' % cxx_compiler
                       ]

            if spec.satisfies('+tests'):
                options.extend(['-DUNIT_TESTS:BOOL=ON',
                                '-DFUNCTIONAL_TESTS:BOOL=ON'])
            else:
                options.extend(['-DUNIT_TESTS:BOOL=OFF',
                                '-DFUNCTIONAL_TESTS:BOOL=OFF'])

            if spec.satisfies('+report'):
                options.extend(['-DENABLE_REPORTINGLIB:BOOL=ON'])

            if spec.satisfies('@hdf'):
                options.extend(['-DENABLE_HDF5:BOOL=ON',
                                '-DZLIB_ROOT=%s' % spec['zlib'].prefix,
                                '-DENABLE_ZLIB_LINK:BOOL=ON'])
            else:
                options.extend(['-DENABLE_HDF5:BOOL=OFF'])

            if spec.satisfies('~mpi'):
                options.extend(['-DENABLE_MPI:BOOL=OFF'])

            if spec.satisfies('~openmp'):
                options.extend(['-DCORENEURON_OPENMP:BOOL=OFF'])

            if spec.satisfies('+gpu'):
                gcc = which("gcc")
                options.extend(['-DCUDA_HOST_COMPILER=%s' % gcc,
                                '-DCUDA_PROPAGATE_HOST_FLAGS=OFF',
                                '-DENABLE_SELECTIVE_GPU_PROFILING=ON',
                                '-DENABLE_OPENACC=ON',
                                '-DENABLE_OPENACC_INFO=ON'])
                # PGI compiler not able to compile nrnreport.cpp when enabled
                # OpenMP, OpenACC and Reporting. Disable ReportingLib for GPU
                options.extend(['-DENABLE_REPORTINGLIB:BOOL=OFF'])

            # tqperf test in perfmodels use net_move functionality which
            # requires use of splay tree instead of default priority queue.
            if spec.satisfies('@perfmodels'):
                options.extend(['-DENABLE_SPLAYTREE_QUEUING=ON'])

            mech_dir_set = False
            modlib_dir = ''

            if 'MOD_FILE_DIR' in os.environ:
                modlib_dir = os.environ['MOD_FILE_DIR']
                mech_dir_set = True
                if not os.path.isdir(modlib_dir):
                    raise RuntimeError("MOD_FILE_DIR environment variable set but directory doesn't exist!")

            if spec.satisfies('@perfmodels'):
                modlib_dir = self.nrnperf_modfiles
                mech_dir_set = True
            elif spec.satisfies('+neurodamusmod'):
                neurodamus_dir = self.spec['neurodamus'].prefix
                modlib_dir = '%s;%s/lib/modlib' % (modlib_dir, neurodamus_dir)
                modfile_list = '%s/lib/modlib/coreneuron_modlist.txt' % (neurodamus_dir)

                options.extend(['-DADDITIONAL_MECHS=%s' % (modfile_list)])
                mech_dir_set = True

            if mech_dir_set:
                options.extend(['-DADDITIONAL_MECHPATH=%s' % (modlib_dir)])

            cmake('..', *options)
            self.profiling_wrapper_on()
            make()
            make('install')
            self.profiling_wrapper_off()

    def setup_environment(self, spack_env, run_env):
        exe = '%s/coreneuron_exec' % self.prefix.bin
        run_env.set('CORENEURON_EXE', exe)

        # for mvapich2 module we need to setup MV2_ENABLE_AFFINITY
        # env variable to turn on multi-threading support
        run_env.set('MV2_ENABLE_AFFINITY', '0')
