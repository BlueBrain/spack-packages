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

    """
    MOD2C is NMODL to C converter adapted for CoreNEURON simulator.
    More information about NMODL can be found NEURON simulator
    documentation at Yale University.
    """

    homepage = "https://github.com/BlueBrain/mod2c"
    url      = "ssh://bbpcode.epfl.ch/sim/mod2c"

    version('develop', git='ssh://bbpcode.epfl.ch/sim/mod2c')

    depends_on('cmake@2.8.12:', type='build')

    def install(self, spec, prefix):

        with working_dir("spack-build", create=True):
            cmake('..', '-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix)
            make()
            make('install')
