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
import sys, shutil

class Neurodamus(Package):

    """
    Library of channels developed by Blue Brain Project, EPFL
    """

    homepage = "ssh://bbpcode.epfl.ch/sim/neurodamus/bbp"
    url      = "ssh://bbpcode.epfl.ch/sim/neurodamus/bbp"

    version('develop', git='ssh://bbpcode.epfl.ch/sim/neurodamus/bbp', branch='sandbox/kumbhar/corebluron_h5')

    #mandatory dependencies
    depends_on("mpi")
    depends_on("hdf5")
    depends_on("neuron")
    depends_on('reportinglib')

    def install(self, spec, prefix):

        shutil.copytree('lib', '%s/lib' % (prefix), symlinks=False)

        with working_dir(prefix):

            modlib = 'lib/modlib'
            nrnivmodl = which('nrnivmodl')
            compile_flags = ''

            #on os-x there is no mallinfo
            if(sys.platform == 'darwin'):
                compile_flags += '-DDISABLE_MALLINFO'

            nrnivmodl('-incflags', compile_flags, modlib)

    def setup_environment(self, spack_env, run_env):
        arch = self.spec.architecture.target
        run_env.prepend_path('PATH', join_path(self.prefix, arch))
        run_env.set('HOC_LIBRARY_PATH', join_path(self.prefix, 'lib/hoclib'))
