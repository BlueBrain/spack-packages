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
from spack.pkg.bbp.neuron import Neuron


class NeuronNmodl(Neuron):

    """NEURON package used in cross compiling environment
    where we want nocmodl to be beuilt for front-end arch"""

    depends_on('automake', type='build')
    depends_on('autoconf', type='build')
    depends_on('libtool', type='build')
    depends_on('pkg-config', type='build', when=sys.platform != 'darwin')
    depends_on('pkg-config%clang', type='build', when=sys.platform == 'darwin')

    def install(self, spec, prefix):

        build = Executable('./build.sh')
        build()

        # we are not setting specific CC, CXX compilers
        # but typically most of the system will have gcc/g++
        # which are for front-end arch
        options = ['--prefix=%s' % prefix,
                   '--with-nmodl-only',
                   '--without-x']

        configure(*options)
        make()
        make('install')
