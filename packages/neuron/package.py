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

    version('master', hg='http://www.neuron.yale.edu/hg/neuron/nrn')

    #always patch build.sh with m4 macro paths for libtool
    patch('build.patch')

    variant('mpi', default=True,
                        description='Enable distributed memory parallelism')

    depends_on('automake', type='build')
    depends_on('autoconf', type='build')
    depends_on('libtool', type='build')
    depends_on('mpi', when='+mpi')

    #on osx platform, pkg-config can't be built without clang
    depends_on('pkg-config', type='build', when=sys.platform != 'darwin')
    depends_on('pkg-config%clang', type='build', when=sys.platform == 'darwin')

    def install(self, spec, prefix):

        build = Executable('./build.sh')
        build()

        #with working_dir("spack-build", create=True):
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

        configure(*options)
        make()
        make('install')
