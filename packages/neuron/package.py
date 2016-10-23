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
    url      = "http://www.neuron.yale.edu/ftp/neuron/versions/v7.4/nrn-7.4.tar.gz"
    list_url = "http://www.neuron.yale.edu/ftp/neuron/versions/"
    list_depth = 2

    # version('develop', git='https://github.com/nrnhines/nrn.git', preferred=True)
    version('develop', git='https://github.com/nrnhines/nrn-hg2git.git',
            preferred=True)
    version('hdf', git='ssh://bbpcode.epfl.ch/user/kumbhar/neuron',
            branch='bbpcode_trunk')

    variant('mpi', default=True, description='Enable MPI parallelism')
    variant('python', default=True, description='Enable python')
    variant('static', default=False, description='Build static libraries')
    variant('cross-compile', default=False, description='Build for cross-compile environment')

    depends_on('automake', type='build')
    depends_on('autoconf', type='build')
    depends_on('libtool', type='build')
    depends_on('mpi', when='+mpi')
    depends_on("nrnh5", when='@hdf')
    depends_on('hdf5', when='@hdf')
    depends_on('python', when='+python')
    depends_on('neuron-nmodl', when='+cross-compile', type='build')

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
                            'CC=%s' % self.compiler.cc,
                            'CXX=%s' % self.compiler.cxx,
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

    def pre_make(self, spec):
        if spec.satisfies('+cross-compile'):
            nocmodl_prefix = spec['neuron-nmodl'].prefix
            sub_dir = self.get_neuron_arch_dir()
            src_nocmodl = '%s/%s/bin/nocmodl' % (nocmodl_prefix, sub_dir)
            dest_nrn_dir = '%s/src/nmodl/' % os.getcwd()
            dest_prefix_dir = '%s/%s/bin/' % (spec.prefix, sub_dir)
            install(src_nocmodl, dest_nrn_dir)
            mkdirp(dest_prefix_dir)
            install(src_nocmodl, dest_prefix_dir)

    # options for hdf5 branch
    def get_hdf5_options(self, spec):
        options = []
        if spec.satisfies('@hdf'):
            compiler_flags = '-DCORENEURON_HDF5=1 -I%s -I%s' % (spec['nrnh5'].include_path, spec['hdf5'].prefix.include)
            link_library = '%s -lhdf5' % (spec['nrnh5'].link_library)
            ld_flags = '-L%s -L%s' % (spec['nrnh5'].prefix.lib, spec['hdf5'].prefix.lib)

            options.extend(['CFLAGS=%s' % compiler_flags])
            options.extend(['CXXFLAGS=%s' % compiler_flags])
            options.extend(['LIBS= %s %s' % (ld_flags, link_library)])

        return options

    def get_python_options(self, spec):
        options = []

        if spec.satisfies('+python'):
            options.extend(['--with-nrnpython', '--disable-pysetup'])

            if spec.satisfies('+cross-compile'):
                py_prefix = spec['python'].prefix
                py_version_string = 'python{0}'.format(spec['python'].version.up_to(2))
                py_lib = spec['python'].prefix.lib64

                options.extend(['PYINCDIR=%s/include/%s' %
                                (py_prefix, py_version_string),
                                'PYLIB=-L%s -l%s' %
                                (py_lib, py_version_string),
                                'PYLIBDIR=%s' % py_lib,
                                'PYLIBLINK=-L%s -l%s' %
                                (py_lib, py_version_string)])
        else:
            options.extend(['--without-nrnpython'])
        return options

    def get_mpi_options(self, spec):
        if spec.satisfies('+mpi'):
            return ['--with-paranrn']
        else:
            return ['--without-paranrn']

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
        return options

    def install(self, spec, prefix):

        options = ['--prefix=%s' % prefix,
                   '--without-iv',
                   '--disable-rx3d']

        options.extend(self.get_configure_options(spec))
        build = Executable('./build.sh')
        build()

        self.pre_make(spec)

        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):
            source_directory = self.stage.source_path
            config = Executable(join_path(source_directory, 'configure'))
            config(*options)
            make()
            make('install')

    def setup_environment(self, spack_env, run_env):
        arch = self.get_neuron_arch_dir()
        run_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))
        self.spec.archdir = arch

    def setup_dependent_environment(self, spack_env, run_env, extension_spec):
        arch = self.get_neuron_arch_dir()
        spack_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))
        self.spec.archdir = arch
