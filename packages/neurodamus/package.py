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

    version('master',      git=url, preferred=True)
    version('coreneuron',  git=url, branch='coreneuronsetup')
    version('hippocampus', git=url, branch='sandbox/kumbhar/hippocampus')
    version('plasticity',  git=url, branch='sandbox/kumbhar/saveupdate_v6support')
    version('simplification', git=url, branch='sandbox/roessert/MegaPaperCompatibility_simplification')

    # version being tested for incite and coreneuron
    version('gpu',      git=url, branch='sandbox/kumbhar/coreneuronsetup_gpu')
    version('parspike', git=url, branch='sandbox/kumbhar/parspike')
    version('plasticitymapping', git=url, branch='sandbox/king/saveupdate')

    variant('special', default=True, description='Compile & create special using nrnivmodl')
    variant('profile', default=False, description="Enable profiling using Tau")

    # basic dependencies
    depends_on("hdf5",   when='+special')
    depends_on("zlib",   when='+special')
    depends_on("neuron", when='+special')
    depends_on("mpi",    when='+special')
    depends_on('reportinglib', when='+special')

    # when we want to profile
    depends_on('tau', when='+profile')

    # additional neuron variant selections
    depends_on("neuron~shared+profile", when='+special+profile')

    # additional reportinglib selections
    depends_on('reportinglib@mapping', when='@plasticitymapping+special')
    depends_on('reportinglib+profile', when='+special+profile')

    # develop version is for coreneuron which needs neuron compiled with python
    conflicts('^neuron~python', when='@coreneuron+special')

    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def install(self, spec, prefix):
        # copy lib directory containing modlib and hoclib
        shutil.copytree('lib', '%s/lib' % (prefix), symlinks=False)

        if spec.satisfies('+special'):
            with working_dir(prefix):
                modlib = 'lib/modlib'
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
                nrnivmodl = which('nrnivmodl')
                nrnivmodl('-incflags', compile_flags,
                          '-loadflags', link_flags, modlib)
                self.profiling_wrapper_off()

    @run_after('install')
    def check_install(self):
        if self.spec.satisfies('+special'):
            # after install check if special is created
            special = '%s/special' % join_path(self.prefix, self.nrnarchdir)
            if not os.path.isfile(special):
                raise RuntimeError("Neurodamus installion check failed!")

    def setup_environment(self, spack_env, run_env):
        if self.spec.satisfies('+special'):
            run_env.prepend_path('PATH', join_path(self.prefix, self.nrnarchdir))
            run_env.set('HOC_LIBRARY_PATH', join_path(self.prefix, 'lib/hoclib'))
