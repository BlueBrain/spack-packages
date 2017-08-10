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


class Mod2c(Package):

    """MOD2C is NMODL to C converter adapted for CoreNEURON simulator.
    More information about NMODL can be found NEURON simulator
    documentation at Yale University."""

    homepage = "https://github.com/BlueBrain/mod2c"
    url      = "https://github.com/BlueBrain/mod2c.git"

    # additional repo paths if any
    bbp_url = "ssh://bbpcode.epfl.ch/sim/mod2c"

    version('develop', git=url, preferred=True)
    version('devopt', git=bbp_url, branch='sandbox/kumbhar/dev')

    depends_on('cmake@2.8.12:', type='build')

    def install(self, spec, prefix):

        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):

            options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                       '-DCMAKE_C_COMPILER=%s' % spack_cc,
                       '-DCMAKE_CXX_COMPILER=%s' % spack_cxx]

            cmake('..', *options)
            make()
            make('install')
