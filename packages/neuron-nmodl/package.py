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


class NeuronNmodl(Package):

    """NEURON's nocmodl for cross compiling environment"""

    homepage = "https://www.neuron.yale.edu/"
    url      = "http://www.neuron.yale.edu/ftp/neuron/versions/v7.4/nrn-7.4.tar.gz"
    list_url = "http://www.neuron.yale.edu/ftp/neuron/versions/"
    list_depth = 2

    version('develop', hg='http://www.neuron.yale.edu/hg/neuron/nrn')

    depends_on('automake', type='build')
    depends_on('autoconf', type='build')
    depends_on('libtool', type='build')

    # on osx platform, pkg-config can't be built without clang
    depends_on('pkg-config', type='build', when=sys.platform != 'darwin')
    depends_on('pkg-config%clang', type='build', when=sys.platform == 'darwin')

    def patch(self):
        # neuron use aclocal which should have proper include paths
        # this is only required on osx but doesn't hurt on other platforms
        pkgconfig_inc = '-I %s/share/aclocal/' % (self.spec['pkg-config'].prefix)
        libtool_inc = '-I %s/share/aclocal/' % (self.spec['libtool'].prefix)
        replace_string = 'aclocal -I m4 %s %s' % (pkgconfig_inc, libtool_inc)

        filter_file(r'aclocal -I m4', r'%s' % replace_string, "build.sh")

    def get_neuron_arch_dir(self):
        arch = self.spec.architecture.target
        return arch

    @when('arch=bgq-redhat6-ppc64')
    def get_neuron_arch_dir(self):
        return 'powerpc64'

    def install(self, spec, prefix):

        build = Executable('./build.sh')
        build()

        options = ['--prefix=%s' % prefix,
                   '--with-nmodl-only',
                   '--without-x']

        # on os-x disable building carbon
        if(sys.platform == 'darwin'):
            options.extend(['macdarwin=no'])

        configure(*options)
        make()
        make('install')

    def setup_environment(self, spack_env, run_env):
        arch = self.get_neuron_arch_dir()
        run_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))

    def setup_dependent_environment(self, spack_env, run_env, extension_spec):
        arch = self.get_neuron_arch_dir()
        spack_env.prepend_path('PATH', join_path(self.prefix, arch, 'bin'))
