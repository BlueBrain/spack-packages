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
import sys

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

    variant('mpi', default=True,
                        description='Enable distributed memory parallelism')
    variant('hdf5', default=False, description='Enable HDF5 interface')

    depends_on('automake', type='build')
    depends_on('autoconf', type='build')
    depends_on('libtool', type='build')
    depends_on('mpi', when='+mpi')
    depends_on("nrnh5", when='+hdf5')
    depends_on('hdf5', when='+hdf5')

    #on osx platform, pkg-config can't be built without clang
    depends_on('pkg-config', type='build', when=sys.platform != 'darwin')
    depends_on('pkg-config%clang', type='build', when=sys.platform == 'darwin')

    def patch(self):
        #for coreneuron, remove GLOBAL and TABLE
        filter_file(r'GLOBAL minf', r'RANGE minf', 'src/nrnoc/hh.mod')
        filter_file(r'TABLE minf', r':TABLE minf', "src/nrnoc/hh.mod")

        #neuron use aclocal which should have proper include paths
        pkgconfig_inc = '-I %s/share/aclocal/' % (self.spec['pkg-config'].prefix)
        libtool_inc = '-I %s/share/aclocal/' % (self.spec['libtool'].prefix)
        replace_string = 'aclocal -I m4 %s %s' % (pkgconfig_inc, libtool_inc)

        filter_file(r'aclocal -I m4', r'%s' % replace_string, "build.sh")

    def install(self, spec, prefix):

        build = Executable('./build.sh')
        build()

        options = []
        options.extend(
                ['--prefix=%s' % prefix,
                 '--without-iv',
                 '--without-nrnpython',
                 '--disable-rx3d'
                ])

        if '+mpi' not in spec:
            options.extend(['--without-paranrn'])
        else:
            options.extend(['--with-paranrn'])

        #on os-x disable building carbon 'click' utility which is deprecated
        if(sys.platform == 'darwin'):
            options.extend(['macdarwin=no'])

        #todo: might go into setup_env of nrnh5
        if spec.satisfies('+hdf5'):
            compiler_flags = '-DCORENEURON_HDF5=1 -I%s' % (spec['nrnh5'].include_path)
            link_library = '%s -lhdf5' % (spec['nrnh5'].static_library)
            options.extend(['LIBS=%s' % link_library])
            options.extend(['CFLAGS=%s' % compiler_flags])
            options.extend(['CXXFLAGS=%s' % compiler_flags])

        configure(*options)
        make()
        make('install')

    def setup_environment(self, spack_env, run_env):
	arch = self.spec.architecture.target
        run_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))
