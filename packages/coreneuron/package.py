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


class Coreneuron(CMakePackage):

    """CoreNEURON is a simplified engine for the NEURON simulator
    optimised for both memory usage and computational speed. Its goal
    is to simulate massive cell networks with minimal memory footprint
    and optimal performance."""

    homepage = "https://github.com/BlueBrain/CoreNeuron"
    url      = "https://github.com/BlueBrain/CoreNeuron"
    bbpurl   = "ssh://bbpcode.epfl.ch/sim/coreneuron"

    version('develop',    git=url, preferred=True, submodules=True)
    version('checkpoint', git=url, branch='checkpoint-restart_prototype')

    # TODO: same as develop but for legacy reasons
    version('perfmodels', git=url, submodules=True)

    variant('mpi',           default=True,  description="Enable MPI support")
    variant('openmp',        default=True,  description="Enable OpenMP support")
    variant('neurodamus',    default=True,  description="Build only MOD files from Neurodamus")
    variant('report',        default=True,  description="Enable reports using ReportingLib")
    variant('gpu',           default=False, description="Enable GPU build")
    variant('knl',           default=False, description="Enable KNL specific flags")
    variant('tests',         default=False, description="Enable building tests")
    variant('profile',       default=False, description="Enable profiling using Tau")

    # mandatory dependencies
    depends_on('mpi', when='+mpi')
    depends_on('cuda', when='+gpu')
    depends_on('boost', when='+tests')
    depends_on('reportinglib', when='+report')
    depends_on('cmake@2.8.12:', type='build')
    depends_on('mod2c@checkpoint', type='build', when='@checkpoint')

    # granular dependency selection for neurodamus
    depends_on('neurodamus@coreneuron~special', when='+neurodamus~gpu')
    depends_on('neurodamus@gpu~special', when='+gpu')

    # neuron models for benchmarking
    depends_on('neuronperfmodels@coreneuron', when='@perfmodels')

    # granular dependency selection for profiling
    depends_on('tau', when='+profile')
    depends_on('reportinglib+profile', when='+report+profile')

    @run_before('build')
    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    @run_after ('install')
    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def get_opt_flags(self):
        flags = "-g -O2"

        if 'bgq' in self.spec.architecture and '%xl' in self.spec:
            flags = '-O3 -qtune=qp -qarch=qp -q64 -qhot=simd -qsmp -qthreaded -g'

        if self.spec.satisfies('+knl') and '%intel' in self.spec:
            flags = '-g -xMIC-AVX512 -O3 -qopt-report=5'

        return flags

    def cmake_args(self):
        spec   = self.spec
        optflag = self.get_opt_flags()

        if spec.satisfies('+profile'):
            env['CC']  = 'tau_cc'
            env['CXX'] = 'tau_cxx'
        # for bg-q, our cmake needs mpi compilers as c, cxx compiler
        elif 'bgq' in spec.architecture and spec.satisfies('+mpi'):
            env['CC']  = spec['mpi'].mpicc
            env['CXX'] = spec['mpi'].mpicxx

        options = ['-DCOMPILE_LIBRARY_TYPE=STATIC',
                   '-DCMAKE_C_FLAGS=%s' % optflag,
                   '-DCMAKE_CXX_FLAGS=%s' % optflag,
                   '-DCMAKE_BUILD_TYPE=CUSTOM']

        if 'bgq' in spec.architecture and '%xl' in spec:
            options.append('-DCMAKE_BUILD_WITH_INSTALL_RPATH=1')

        if spec.satisfies('+tests'):
            options.extend(['-DUNIT_TESTS=ON',
                            '-DFUNCTIONAL_TESTS=ON'])
        else:
            options.extend(['-DUNIT_TESTS=OFF',
                            '-DFUNCTIONAL_TESTS=OFF'])

        if spec.satisfies('+report'):
            options.append('-DENABLE_REPORTINGLIB=ON')
        else:
            options.append('-DENABLE_REPORTINGLIB=OFF')

        if spec.satisfies('+mpi'):
            options.append('-DENABLE_MPI=ON')
        else:
            options.append('-DENABLE_MPI=OFF')


        if spec.satisfies('+openmp'):
            options.append('-DCORENEURON_OPENMP=ON')
        else:
            options.append('-DCORENEURON_OPENMP=OFF')

        if spec.satisfies('+gpu'):
            gcc = which("gcc")
            options.extend(['-DCUDA_HOST_COMPILER=%s' % gcc,
                            '-DCUDA_PROPAGATE_HOST_FLAGS=OFF',
                            '-DENABLE_SELECTIVE_GPU_PROFILING=ON',
                            '-DENABLE_OPENACC=ON',
                            '-DENABLE_OPENACC_INFO=ON'])
            # PGI compiler not able to compile nrnreport.cpp when enabled
            # OpenMP, OpenACC and Reporting. Disable ReportingLib for GPU
            options.append('-DENABLE_REPORTINGLIB=OFF')

        # tqperf test in perfmodels use net_move functionality which
        # requires use of splay tree instead of default priority queue.
        if spec.satisfies('@perfmodels'):
            options.append('-DENABLE_SPLAYTREE_QUEUING=ON')

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
        elif spec.satisfies('+neurodamus'):
            neurodamus_dir = self.spec['neurodamus'].prefix
            modlib_dir = '%s;%s/lib/modlib' % (modlib_dir, neurodamus_dir)
            modfile_list = '%s/lib/modlib/coreneuron_modlist.txt' % (neurodamus_dir)

            options.append('-DADDITIONAL_MECHS=%s' % modfile_list)
            mech_dir_set = True

        if mech_dir_set:
            options.append('-DADDITIONAL_MECHPATH=%s' % modlib_dir)

        return options

    def setup_environment(self, spack_env, run_env):
        exe = '%s/coreneuron_exec' % self.prefix.bin
        run_env.set('CORENEURON_EXE', exe)

        # for mvapich2 module we need to setup MV2_ENABLE_AFFINITY
        # env variable to turn on multi-threading support
        run_env.set('MV2_ENABLE_AFFINITY', '0')
