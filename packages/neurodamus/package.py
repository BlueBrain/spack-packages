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
import os
import shutil


class Neurodamus(Package):

    """Library of channels developed by Blue Brain Project, EPFL"""

    homepage = "ssh://bbpcode.epfl.ch/sim/neurodamus/bbp"
    url      = "ssh://bbpcode.epfl.ch/sim/neurodamus/bbp"

    version('master',  git=url)
    version('develop', git=url, branch='coreneuronsetup')
    version('developopt', git=url, branch='sandbox/kumbhar/coreneuronsetupopt')
    version('hdf',     git=url, branch='sandbox/kumbhar/corebluron_h5')
    version('gpu',     git=url, branch='sandbox/kumbhar/coreneuronsetup_gpu')
    version('plasticity', git=url, branch='sandbox/chindemi/glusynapse-master')
    version('oldplasticity', git=url, branch='sandbox/kumbhar/savestate_devel')
    version('saveupdate', git=url, branch='sandbox/king/saveupdate')
    version('saveupdateprofile', git=url, branch='sandbox/kumbhar/saveupdate')

    variant('compile', default=True, description='Compile and create executable using nrnivmodl')
    variant('profile', default=False, description="Enable profiling using Tau")
    variant('debug',   default=False, description="Build debug version")

    depends_on("hdf5", when='+compile')
    depends_on("zlib", when='+compile')
    depends_on("neuron", when='+compile')
    depends_on('tau', when='+profile')
    depends_on("neuron+debug", when='+compile+debug')
    depends_on("neuron+profile", when='+compile+profile')
    depends_on("neuron@hdf", when='@hdf+compile')
    depends_on("neuron@oldplasticity", when='@oldplasticity+compile')
    depends_on('reportinglib', when='+compile')
    depends_on('reportinglib+debug', when='+compile+debug')
    depends_on('reportinglib+profile', when='+compile+profile')
    depends_on("mpi", when='+compile')

    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def install(self, spec, prefix):

        shutil.copytree('lib', '%s/lib' % (prefix), symlinks=False)

        if spec.satisfies('+compile'):

            with working_dir(prefix):

                modlib = 'lib/modlib'
                nrnivmodl = which('nrnivmodl')

                extra_flags = ''

                if spec.satisfies('+profile'):
                    extra_flags += ' -DENABLE_TAU_PROFILER'

                compile_flags = '-I%s -I%s %s' % (spec['reportinglib'].prefix.include,
                                                  spec['hdf5'].prefix.include,
                                                  extra_flags)

                link_flags = '-L%s -lreportinglib -L%s -lhdf5 -L%s -lz' % (
                             spec['reportinglib'].prefix.lib64,
                             spec['hdf5'].prefix.lib,
                             spec['zlib'].prefix.lib)

                self.profiling_wrapper_on()
                nrnivmodl('-incflags', compile_flags,
                          '-loadflags', link_flags, modlib)
                self.profiling_wrapper_off()

                self.check_install(spec)

    def check_install(self, spec):
        special = '%s/special' % join_path(self.prefix, self.archdir)
        if not os.path.isfile(special):
            raise RuntimeError("Neurodamus installion check failed!")

    def setup_environment(self, spack_env, run_env):
        if self.spec.satisfies('+compile'):
            run_env.prepend_path('PATH', join_path(self.prefix, self.archdir))
            run_env.set('HOC_LIBRARY_PATH', join_path(self.prefix, 'lib/hoclib'))
