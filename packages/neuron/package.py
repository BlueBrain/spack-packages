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
import os, sys
import shutil


class Neuron(Package):

    """
    NEURON simulation environment
    """

    homepage = "https://www.neuron.yale.edu/"
    url      = "http://www.neuron.yale.edu/ftp/neuron/versions/v7.4/nrn-7.4.tar.gz"
    list_url = "http://www.neuron.yale.edu/ftp/neuron/versions/"
    list_depth = 2

    #version('yale', hg='http://www.neuron.yale.edu/hg/neuron/nrn')
    version('develop', git='ssh://bbpcode.epfl.ch/user/kumbhar/neuron', branch='bbpcode_trunk')

    #patch is  trivial so handle it in patch()
    #patch('build.patch')

    variant('mpi', default=True, description='Enable distributed memory parallelism')
    variant('python', default=True, description='Enable python')
    variant('hdf5', default=False, description='Enable HDF5 interface')
    variant('with-nmodlonly', default=False, description='Also use nmodl-only installation')

    depends_on('automake', type='build')
    depends_on('autoconf', type='build')
    depends_on('libtool', type='build')
    depends_on('mpi', when='+mpi')
    depends_on("nrnh5", when='+hdf5')
    depends_on('hdf5', when='+hdf5')
    depends_on('python', when='+python')
    depends_on('neuron-nmodl', when='+with-nmodlonly', type='build')

    #on osx platform, pkg-config can't be built without clang
    depends_on('pkg-config', type='build', when=sys.platform != 'darwin')
    depends_on('pkg-config%clang', type='build', when=sys.platform == 'darwin')

    def patch(self):
        #for coreneuron, remove GLOBAL and TABLE
        filter_file(r'GLOBAL minf', r'RANGE minf', 'src/nrnoc/hh.mod')
        filter_file(r'TABLE minf', r':TABLE minf', "src/nrnoc/hh.mod")

        #neuron use aclocal which should have proper include paths
        #this is only required on osx but doesn't hurt on other platforms
        pkgconfig_inc = '-I %s/share/aclocal/' % (self.spec['pkg-config'].prefix)
        libtool_inc = '-I %s/share/aclocal/' % (self.spec['libtool'].prefix)
        replace_string = 'aclocal -I m4 %s %s' % (pkgconfig_inc, libtool_inc)

        filter_file(r'aclocal -I m4', r'%s' % replace_string, "build.sh")

    def get_cross_compile_options(self, spec):
        return []

    @when('arch=bgq-CNK-ppc64')
    def get_cross_compile_options(self, spec):
        return ['--enable-bluegeneQ',
                '--host=powerpc64',
                '--without-memacs']

    def get_neuron_arch_dir(self):
        arch = self.spec.architecture.target
        return arch

    @when('arch=bgq-CNK-ppc64')
    def get_neuron_arch_dir(self):
        return 'powerpc64'

    def pre_make(self, spec):
        if spec.satisfies('+with-nmodlonly'):
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
        if spec.satisfies('+hdf5'):
            compiler_flags = '-DCORENEURON_HDF5=1 -I%s' % (spec['nrnh5'].include_path)
            link_library = '%s -lhdf5' % (spec['nrnh5'].link_library)

            options.extend(['CFLAGS=%s' % compiler_flags])
            options.extend(['CXXFLAGS=%s' % compiler_flags])

            options.extend(['LIBS=%s' % link_library])
            options.extend(['LDFLAGS=-L%s -L%s' % (spec['nrnh5'].prefix.lib, spec['hdf5'].prefix.lib)])
        return options

    def get_python_options(self, spec):
        options = []
        if spec.satisfies('+python'):
            py_prefix = spec['python'].prefix
            py_version_string = 'python{0}'.format(spec['python'].version.up_to(2))
            py_include = join_path('include', py_version_string)
            py_lib = spec['python'].prefix.lib64

            options.extend([
                        '--with-nrnpython',
                        'PYINCDIR=%s/include/%s' % (py_prefix, py_version_string),
                        'PYLIB=-L%s -l%s' % (py_lib, py_version_string),
                        'PYLIBDIR=%s' % py_lib,
                        'PYLIBLINK=-L%s -l%s' % (py_lib, py_version_string)
                    ])
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
        if spec.satisfies('+with-nmodlonly'):
            options.extend(self.get_cross_compile_options(spec))
        options.extend(self.get_hdf5_options(spec))
        options.extend(self.get_python_options(spec))
        options.extend(self.get_mpi_options(spec))
        return options


    def install(self, spec, prefix):

        options = [
                 '--prefix=%s' % prefix,
                 '--without-iv',
                 '--disable-rx3d'
                ]

        options.extend(self.get_configure_options(spec))
        build = Executable('./build.sh')
        build()

        #on os-x disable building carbon 'click' utility which is deprecated
        if(sys.platform == 'darwin'):
            options.extend(['macdarwin=no'])

        self.pre_make(spec)
        configure(*options)
        make()
        make('install')

    def setup_environment(self, spack_env, run_env):
	arch = self.get_neuron_arch_dir()
        run_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))

    def setup_dependent_environment(self, spack_env, run_env, extension_spec):
	arch = self.get_neuron_arch_dir()
        spack_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))
        self.spec.archdir = arch
