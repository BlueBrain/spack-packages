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


class Servus(CMakePackage):

    """Zeroconf discovery in C++"""

    homepage = "https://github.com/HBPVIS/Servus"
    url      = "https://github.com/HBPVIS/Servus.git"

    version('1.5.1',   git=url, tag='1.5.1', submodules=True)
    version('1.5.0',   git=url, tag='1.5.0', submodules=True)
    version('1.4.0',   git=url, tag='1.4.0', submodules=True)
    version('develop', git=url, submodules=True)

    depends_on('qt@5.4:')
    depends_on('boost@1.54:')
    depends_on('cmake@3:', type='build')
