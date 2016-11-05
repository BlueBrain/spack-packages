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
import sys


class Neuron(Package):

    """NEURON simulation environment"""

    homepage = "https://www.neuron.yale.edu/"

    version('develop', git='https://github.com/pramodk/nrn.git', preferred=True)
    version('hdf', git='ssh://bbpcode.epfl.ch/user/kumbhar/neuron', branch='bbpcode_trunk')

    variant('mpi', default=True, description='Enable MPI parallelism')
    variant('python', default=True, description='Enable python')
    variant('static', default=True, description='Build static libraries')
    variant('cross-compile', default=False, description='Build for cross-compile environment')

    depends_on('automake', type='build')
    depends_on('autoconf', type='build')
    depends_on('libtool', type='build')
    depends_on('mpi', when='+mpi')
    depends_on("nrnh5", when='@hdf')
    depends_on('python@2.6:', when='+python')

    # on osx platform, pkg-config can't be built without clang
    depends_on('pkg-config', type='build', when=sys.platform != 'darwin')
    depends_on('pkg-config%clang', type='build', when=sys.platform == 'darwin')

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
                            'MPICC=%s' % self.compiler.cc,
                            'MPICXX=%s' % self.compiler.cxx])
        return options

    def get_neuron_arch_dir(self):
        arch = self.spec.architecture.target

        if 'bgq' in self.spec.architecture:
            arch = 'powerpc64'
        if 'cray' in self.spec.architecture:
            arch = 'x86_64'
        return arch

    # options for hdf5 branch
    def get_hdf5_options(self, spec):
        options = []
        if spec.satisfies('@hdf'):
            compiler_flags = '-O3 -DCORENEURON_HDF5=1 %s' % spec['nrnh5'].include_path
            link_library = '%s' % spec['nrnh5'].link_library

            options.extend(['CFLAGS=%s' % compiler_flags])
            options.extend(['CXXFLAGS=%s' % compiler_flags])
            options.extend(['LIBS=%s' % link_library])
        return options

    def get_python_options(self, spec):
        options = []

        if spec.satisfies('+python'):
            py_prefix = spec['python'].prefix
            py_version_string = 'python{0}'.format(spec['python'].version.up_to(2))
            python_exec = '%s/bin/%s' % (py_prefix, py_version_string)

            options.extend(['--with-nrnpython=%s' % python_exec, '--disable-pysetup'])

            if spec.satisfies('+cross-compile'):
                py_lib = spec['python'].prefix.lib64

                options.extend(['PYINCDIR=%s/include/%s' % (py_prefix, py_version_string),
                                'PYLIB=-L%s -l%s' % (py_lib, py_version_string),
                                'PYLIBDIR=%s' % py_lib,
                                'PYLIBLINK=-L%s -l%s' % (py_lib, py_version_string)])
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

        # pgi has proble with compiling neuron in static mode
        # even for static variant, build shared
        if spec.satisfies('%pgi'):
            options.extend(['CFLAGS=-fPIC -O3',
                            'CXXFLAGS=-fPIC -O3',
                            '--enable-shared'])
        else:
            options.extend(['CFLAGS=-O3', 'CXXFLAGS=-O3'])

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
        gcc = which("gcc")
        gplusplus = which("g++")

        options = ['--prefix=%s' % prefix,
                   '--with-nmodl-only',
                   '--without-x',
                   'CC=%s' % gcc,
                   'CXX=%s' % gplusplus]

        source = self.stage.source_path
        configure = Executable(join_path(source, 'configure'))
        configure(*options)
        make()
        make('install')

    def install(self, spec, prefix):

        options = ['--prefix=%s' % prefix,
                   '--without-iv',
                   '--disable-rx3d',
                   'CC=%s' % spack_cc,
                   'CXX=%s' % spack_cxx]

        options.extend(self.get_configure_options(spec))
        build = Executable('./build.sh')
        build()

        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):

            if spec.satisfies('+cross-compile'):
                self.build_nmodl(spec, prefix)

            source_directory = self.stage.source_path
            configure = Executable(join_path(source_directory, 'configure'))
            configure(*options)
            make()
            make('install')

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
