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
import os
import shutil


class Neurodamus(Package):

    """Library of channels developed by Blue Brain Project, EPFL"""

    homepage = "ssh://bbpcode.epfl.ch/sim/neurodamus/bbp"
    url      = "ssh://bbpcode.epfl.ch/sim/neurodamus/bbp"

    version('master',  git=url)
    version('develop', git=url, branch='coreneuronsetup')
    version('hdf',     git=url, branch='sandbox/kumbhar/corebluron_h5')
    version('gpu',     git=url, branch='sandbox/kumbhar/coreneuronsetup_gpu')

    variant('compile', default=True, description='Compile and create executable using nrnivmodl')

    depends_on("hdf5", when='+compile')
    depends_on("neuron", when='+compile')
    depends_on("neuron@hdf", when='@hdf+compile')
    depends_on('reportinglib', when='+compile')
    depends_on("mpi", when='+compile')

    def install(self, spec, prefix):

        shutil.copytree('lib', '%s/lib' % (prefix), symlinks=False)

        if spec.satisfies('+compile'):

            with working_dir(prefix):

                modlib = 'lib/modlib'
                nrnivmodl = which('nrnivmodl')
                compile_flags = '-I%s -I%s' % (spec['reportinglib'].prefix.include,
                                               spec['hdf5'].prefix.include)
                link_flags = '-L%s -lreportinglib -L%s -lhdf5' % (
                             spec['reportinglib'].prefix.lib64,
                             spec['hdf5'].prefix.lib)

                # on os-x there is no mallinfo
                if(sys.platform == 'darwin'):
                    compile_flags += ' -DDISABLE_MALLINFO'

                nrnivmodl('-incflags', compile_flags,
                          '-loadflags', link_flags, modlib)

                self.check_install(spec)

    def check_install(self, spec):
        special = '%s/special' % join_path(self.prefix, self.archdir)
        if not os.path.isfile(special):
            raise RuntimeError("Neurodamus installion check failed!")

    def setup_environment(self, spack_env, run_env):
        if self.spec.satisfies('+compile'):
            run_env.prepend_path('PATH', join_path(self.prefix, self.archdir))
            run_env.set('HOC_LIBRARY_PATH', join_path(self.prefix, 'lib/hoclib'))
