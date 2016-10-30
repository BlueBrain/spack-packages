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
import glob
import shutil


class Neuronperfmodels(Package):

    """Collection models for NEURON / CoreNeuron performance benchmarking"""

    homepage = "ssh://bbpcode.epfl.ch/user/kumbhar/nrnperfmodels"
    url      = "ssh://bbpcode.epfl.ch/user/kumbhar/nrnperfmodels"

    version('1.0', git='ssh://bbpcode.epfl.ch/user/kumbhar/nrnperfmodels', submodules=True)

    depends_on('reportinglib')
    depends_on("neuron")
    depends_on("hdf5")

    def arch_specific_flags(self):
        flags = ''

        # on os-x there is no mallinfo
        if(sys.platform == 'darwin'):
            flags += ' -DDISABLE_MALLINFO'

        return flags

    def neurodamus_flags(self, spec):
        reporting_inc = spec['reportinglib'].prefix.include
        reporting_lib = spec['reportinglib'].prefix.lib64
        hdf5_inc = spec['hdf5'].prefix.include
        hdf5_lib = spec['hdf5'].prefix.lib

        incflags = '-I%s -I%s' % (reporting_inc, hdf5_inc)
        ldflags = '-L%s -lreportinglib -L%s -lhdf5' % (reporting_lib, hdf5_lib)

        return incflags, ldflags

    def check_install(self):
        special = '%s/special' % self.archdir
        if not os.path.isfile(special):
            raise RuntimeError("Installation check failed (%s)!" % special)

    def create_special(self, incflags, ldflags, modir):
        nrnivmodl = which('nrnivmodl')
        nrnivmodl('-incflags', incflags, '-loadflags', ldflags, modir)
        self.check_install()

    def build_neurodamus(self, spec, prefix):
        src = '%s/neurodamus/lib' % self.stage.source_path
        dest = '%s/neurodamus/lib' % prefix
        install_tree(src, dest, symlinks=False)

        with working_dir(dest):
            incflags, ldflags = self.neurodamus_flags(spec)
            cflags = '%s %s' % (incflags, self.arch_specific_flags())
            self.create_special(cflags, ldflags, 'modlib')

    def build_nrntraub(self, spec, prefix):
        src = '%s/nrntraub' % self.stage.source_path
        dest = '%s/nrntraub' % prefix
        install_tree(src, dest, symlinks=False)

        with working_dir(dest):
            os.remove('mod/ri.mod')
            self.create_special('', '', 'mod')

    def build_dentate(self, spec, prefix):
        src = '%s/reduced_dentate' % self.stage.source_path
        dest = '%s/reduced_dentate' % prefix
        install_tree(src, dest, symlinks=False)

        with working_dir(dest):
            self.create_special('', '', 'mechanisms')

    def build_ringtest(self, spec, prefix):
        src = '%s/ringtest' % self.stage.source_path
        dest = '%s/ringtest' % prefix
        install_tree(src, dest, symlinks=False)

    def build_tqperf(self, spec, prefix):
        src = '%s/tqperf' % self.stage.source_path
        dest = '%s/tqperf' % prefix
        install_tree(src, dest, symlinks=False)

        with working_dir(dest):
            os.mkdir('mod')
            for file in glob.glob(r'*.mod'):
                shutil.copy(file, 'mod/')
            self.create_special('', '', 'mod')

    def copy_compatible_mod_files(self, spec, path):
        os.mkdir(path)

        modfilepath = '%s/neurodamus/lib/modlib/coreneuron_modlist.txt' % self.stage.source_path
        with open(modfilepath) as f:
                neurodamus_modfiles = f.read().splitlines()

        for root, dirnames, filenames in os.walk(self.stage.source_path):
            for filename in filenames:
                if filename.endswith(('.mod', '.inc')):
                    filepath = os.path.join(root, filename)
                    if 'nrntraub/mod/ri.mod' in filepath:
                        continue
                    if '/neurodamus/lib' in filepath and os.path.basename(filepath) not in neurodamus_modfiles:
                        continue
                    shutil.copy(filepath, path)

    def build_single_exec(self, spec, prefix):
        with working_dir(prefix):
            modpath = 'modfiles'
            self.copy_compatible_mod_files(spec, modpath)
            incflags, ldflags = self.neurodamus_flags(spec)
            cflags = '%s %s' % (incflags, self.arch_specific_flags())
            self.create_special(cflags, ldflags, modpath)

            # for coreneuron, we need exp2syn.mod file from NEURON
            ex2syn = '%s/mod/exp2syn.mod' % spec['neuron'].prefix
            shutil.copy(ex2syn, modpath)

    def install(self, spec, prefix):
        self.build_neurodamus(spec, prefix)
        self.build_nrntraub(spec, prefix)
        self.build_dentate(spec, prefix)
        self.build_ringtest(spec, prefix)
        self.build_tqperf(spec, prefix)
        self.build_single_exec(spec, prefix)

    def setup_environment(self, spack_env, run_env):
        archdir = os.environ['NEURON_ARCH_DIR']
        prefix = self.prefix

        neurodamus_exe = '%s/neurodamus/lib/%s/special' % (prefix, archdir)
        nrntraub_exe = '%s/nrntraub/%s/special' % (prefix, archdir)
        dentate_exe = '%s/reduced_dentate/%s/special' % (prefix, archdir)
        ringtest_exe = '%s/%s/bin/nrniv' % (self.spec['neuron'].prefix, archdir)
        tqperf_exe = '%s/tqperf/%s/special' % (prefix, archdir)
        nrnperf_exe = '%s/%s/special' % (prefix, archdir)
        modfiles = '%s/modfiles' % prefix

        run_env.set('NEURODAMUS_EXE', neurodamus_exe)
        run_env.set('TRAUB_EXE', nrntraub_exe)
        run_env.set('DENTATE_EXE', dentate_exe)
        run_env.set('RINGTEST_EXE', ringtest_exe)
        run_env.set('TQPERF_EXE', tqperf_exe)
        run_env.set('NRNPERF_EXE', nrnperf_exe)
        run_env.set('NRNPERF_MODFILES', modfiles)

    def setup_dependent_package(self, module, dspec):
        dspec.package.nrnperf_modfiles = '%s/modfiles' % self.prefix
