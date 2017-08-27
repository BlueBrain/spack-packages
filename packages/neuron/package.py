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
from llnl.util import tty
import os
import sys
import glob


class Neuron(Package):

    """NEURON simulation environment"""

    homepage = "https://www.neuron.yale.edu/"
    url      = "https://github.com/nrnhines/nrn"

    # TODO: extra urls from development
    devurl   = "https://github.com/pramodk/nrn.git"
    bbpurl   = "ssh://bbpcode.epfl.ch/user/kumbhar/neuron"

    version('master', git=url, preferred=True)
    version('develop', git=devurl)
    version('hdf', git=bbpurl, branch='bbpcode_trunk')

    variant('mpi', default=True, description='Enable MPI parallelism')
    variant('python', default=True, description='Enable python')
    variant('static', default=True, description='Build static libraries')
    variant('cross-compile', default=False, description='Build for cross-compile environment')
    variant('profile',       default=False, description="Enable Tau profiling")
    variant('debug',         default=False, description="Compile without optimization")
    variant('multisend',     default=True, description="Enable multi-send spike exchange")

    depends_on('automake', type='build')
    depends_on('autoconf', type='build')
    depends_on('libtool', type='build')
    depends_on("nrnh5", when='@hdf')
    depends_on('python@2.6:', when='+python')
    depends_on('tau', when='+profile')
    depends_on('mpi', when='+mpi')

    depends_on('pkg-config', type='build')

    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def patch(self):
        # for coreneuron, remove GLOBAL and TABLE
        filter_file(r'GLOBAL minf', r'RANGE minf', 'src/nrnoc/hh.mod')
        filter_file(r'TABLE minf', r':TABLE minf', "src/nrnoc/hh.mod")

        # neuron use aclocal which should have proper include paths
        # this is only required on osx but doesn't hurt on other platforms
        pkgconfig_inc = '-I %s/share/aclocal/' % (self.spec['pkg-config'].prefix)
        libtool_inc = '-I %s/share/aclocal/' % (self.spec['libtool'].prefix)
        replace_string = 'aclocal -I m4 %s %s' % (pkgconfig_inc, libtool_inc)

        filter_file(r'aclocal -I m4', r'%s' % replace_string, "build.sh")

    def get_cross_compile_options(self, spec):
        options = []

        if 'bgq' in self.spec.architecture:
            options.extend(['--enable-bluegeneQ',
                            '--host=powerpc64',
                            '--without-memacs'])

        if 'cray' in self.spec.architecture:
            options.extend(['--without-memacs',
                            '--without-nmodl',
                            'cross_compiling=yes'])
        return options

    def get_optimization_level(self):
        if self.spec.satisfies('+debug'):
            return '-O0 -g'
        elif 'bgq' in self.spec.architecture:
            return '-O3 -qtune=qp -qarch=qp -q64 -qstrict -qnohot -g'
        else:
            return '-O2 -g'

    def get_neuron_arch_dir(self):
        arch = self.spec.architecture.target

        if 'bgq' in self.spec.architecture:
            arch = 'powerpc64'
        if 'cray' in self.spec.architecture:
            arch = 'x86_64'
        if 'ppc64le' in self.spec.architecture:
            arch = 'powerpc64le'
        return arch

    # options for hdf5 branch
    def get_hdf5_options(self, spec):
        options = []

        optflag = self.get_optimization_level()

        if spec.satisfies('@hdf'):
            compiler_flags = '%s -DCORENEURON_HDF5=1 %s' % (optflag, spec['nrnh5'].include_path)
            link_library = '%s' % spec['nrnh5'].link_library

            options.extend(['CFLAGS=%s' % compiler_flags])
            options.extend(['CXXFLAGS=%s' % compiler_flags])
            options.extend(['LIBS=%s' % link_library])
        return options

    def get_python_options(self, spec):
        options = []

        if spec.satisfies('+python'):

            # we could use spec['python'].prefix as install prefix
            # but then external python installations (e.g. brew) have
            # completely different installation hierarchy and hence result in build
            # failure. We have to test below approach in cross compiling
            # environment where we can't execute compute node python on
            # front-end (see #5112 )
            #py_prefix = spec['python'].prefix
            py_prefix = spec['python'].home
            python_exec = spec['python'].command.path

            py_lib = 'python{0}'.format(spec['python'].version.up_to(2))
            py_lib_dir = spec['python'].prefix.lib
            extra_libs = ''

            # todo : bit of hack for argonne bgq system as they have extra
            #        libraries to link. May be adding variant would be better?
            import socket
            if 'bgq' in spec.architecture and 'alcf.anl.gov' in socket.getfqdn():
                extra_libs = '-lz -lssl -lcrypto -lutil'

            # on platform like theta cray, intel python has extra directory include/python3.5m/
            # and hence we need to find directory of Python.h
            files = [y for x in os.walk(py_prefix) for y in glob.glob(os.path.join(x[0], 'Python.h'))]
            if files:
                py_inc_dir = os.path.dirname(files[0])
            else:
                tty.warn('Could not find Python.h in the specified the python prefix'
                         'Make sure to install relevant python dev packages')

            # spack has a method to return python libraries but we need to wait for
            # PR to be merged upstream : https://github.com/LLNL/spack/pull/5118
            files = [y for x in os.walk(py_prefix) for y in glob.glob(os.path.join(x[0], 'libpython*'))]
            if files:
                py_lib_dir = os.path.dirname(files[0])
                # depending on pymalloc enabled or not, python library name might be different
                # check if library name is like libpython2.7m or libpython3.5m etc
                if [libname for libname in files if py_lib+'m' in libname]:
                    py_lib += 'm'
            else:
                tty.warn('Could not find libpython in the specified the python prefix'
                         'Make sure to install relevant python dev packages')

            options.extend(['--with-nrnpython=%s' % python_exec, '--disable-pysetup'])
            options.extend(['PYINCDIR=%s' % (py_inc_dir),
                    'PYLIB=-L%s -l%s %s' % (py_lib_dir, py_lib, extra_libs),
                    'PYLIBDIR=%s' % py_lib_dir,
                    'PYLIBLINK=-L%s -l%s %s' % (py_lib_dir, py_lib, extra_libs)])

            # TODO : neuron has depdendency with backend python as well as front-end
            # while building for python3 we see issue because neuron use python from
            # /usr/bin where PYTHONPATH is for python3 resulting in import errors
            if spec.satisfies('~cross-compile'):
                options.append('PYTHON_BLD=%s' % python_exec)
        else:
            options.extend(['--without-nrnpython'])
        return options

    def get_mpi_options(self, spec):
        if spec.satisfies('+mpi'):
            return ['--with-paranrn']
        else:
            return ['--without-paranrn']

    def get_compiler_options(self, spec):
        options = []

        optflag = self.get_optimization_level()

        # pgi has proble with compiling neuron in static mode
        # even for static variant, build shared
        if spec.satisfies('%pgi'):
            options.extend(['CFLAGS=-fPIC %s' % optflag,
                            'CXXFLAGS=-fPIC %s' % optflag,
                            '--enable-shared'])
        else:
            options.extend(['CFLAGS=%s' % optflag, 'CXXFLAGS=%s' % optflag])

        return options

    def get_configure_options(self, spec):
        options = []

        if spec.satisfies('+static'):
            options.extend(['--disable-shared',
                            'linux_nrnmech=no'])
        # on os-x disable building carbon 'click' utility which is deprecated
        if(sys.platform == 'darwin'):
            options.extend(['macdarwin=no'])

        if spec.satisfies('+cross-compile'):
            options.extend(self.get_cross_compile_options(spec))

        options.extend(self.get_mpi_options(spec))
        options.extend(self.get_python_options(spec))
        options.extend(self.get_hdf5_options(spec))
        options.extend(self.get_compiler_options(spec))
        return options

    def build_nmodl(self, spec, prefix):

        # on cray and bg-q, gcc and g++ are for front-end
        # so it's safe to use those for nocmodl compilation
        c_compiler = which("gcc")
        cxx_compiler = which("g++")

        options = ['--prefix=%s' % prefix,
                   '--with-nmodl-only',
                   '--without-x',
                   'CC=%s' % c_compiler,
                   'CXX=%s' % cxx_compiler]

        source = self.stage.source_path
        configure = Executable(join_path(source, 'configure'))
        configure(*options)
        make()
        make('install')

    def install(self, spec, prefix):

        c_compiler = spack_cc
        cxx_compiler = spack_cxx
        mpi_c_compiler = spack_cc
        mpi_cxx_compiler = spack_cxx

        if spec.satisfies('+mpi'):
            mpi_c_compiler = spec['mpi'].mpicc
            mpi_cxx_compiler = spec['mpi'].mpicxx

        # for bg-q we can't set xlc as CC and CXX
        if 'bgq' in self.spec.architecture:
            c_compiler = spec['mpi'].mpicc
            cxx_compiler = spec['mpi'].mpicxx

        if spec.satisfies('+profile'):
            c_compiler = 'tau_cc'
            cxx_compiler = 'tau_cxx'
            mpi_c_compiler = 'tau_cc'
            mpi_cxx_compiler = 'tau_cxx'

        options = ['--prefix=%s' % prefix,
                   '--without-iv',
                   '--without-x',
                   '--without-readline',
                   '--disable-rx3d',
                   'CC=%s' % c_compiler,
                   'CXX=%s' % cxx_compiler,
                   'MPICC=%s' % mpi_c_compiler,
                   'MPICXX=%s' % mpi_cxx_compiler]

        options.extend(self.get_configure_options(spec))
        build = Executable('./build.sh')
        build()

        # passing -M option to Tau disables instrumentation. Avoid this
        # with below autotools option
        if spec.satisfies('+profile'):
            options.extend(['--disable-dependency-tracking'])

        if spec.satisfies('+multisend'):
            options.extend(['--with-multisend'])

        options.extend(['MPICC=%s' % mpi_c_compiler,
                        'MPICXX=%s' % mpi_cxx_compiler])

        # on cray systems somehow we get error while linking. Even if
        # if we use cc wrapper we get errors. So explicitly add mpich.
        # Also, -pthread is not valid pthread option for cray compiler.
        # As we are not using threads, don't use pthread.
        if 'cray' in self.spec.architecture:
            options.extend(['LIBS=-lmpich',
                            'use_pthread=no'])

        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):
            if spec.satisfies('+cross-compile'):
                self.build_nmodl(spec, prefix)

            source_directory = self.stage.source_path
            configure = Executable(join_path(source_directory, 'configure'))
            configure(*options)
            self.profiling_wrapper_on()
            make()
            make('install')
            self.profiling_wrapper_off()

    @run_after('install')
    def filter_compilers(self):
        """run after install to avoid spack compiler wrappers
        getting embded into nrnivmodl script"""

        arch = self.get_neuron_arch_dir()
        nrnmakefile = join_path(self.prefix, arch, 'bin/nrniv_makefile')

        kwargs = {
            'backup': False,
            'string': True
        }

        filter_file(env['CC'],  self.compiler.cc, nrnmakefile, **kwargs)
        filter_file(env['CXX'], self.compiler.cxx, nrnmakefile, **kwargs)

    def setup_environment(self, spack_env, run_env):
        arch = self.get_neuron_arch_dir()
        run_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))

    def setup_dependent_environment(self, spack_env, run_env, extension_spec):
        arch = self.get_neuron_arch_dir()
        spack_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))

    def setup_dependent_package(self, module, dspec):
        arch = self.get_neuron_arch_dir()
        dspec.package.archdir = arch
        os.environ['NEURON_ARCH_DIR'] = str(arch)
