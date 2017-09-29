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
import glob
import shutil


class Neuronperfmodels(Package):

    """Collection models for NEURON / CoreNeuron performance benchmarking"""

    homepage = "ssh://bbpcode.epfl.ch/user/kumbhar/nrnperfmodels"
    url      = "ssh://bbpcode.epfl.ch/user/kumbhar/nrnperfmodels"

    version('neuron', git=url, submodules=True, preferred=True)
    version('coreneuron', git=url, submodules=True)

    variant('profile', default=False, description="Enable profiling using Tau")

    depends_on('reportinglib',  when='@neuron')
    depends_on('reportinglib+profile',  when='@neuron+profile')
    depends_on('neuron', when='@neuron')
    depends_on('neuron~shared+profile', when='@neuron+profile')
    depends_on('hdf5', when='@neuron')
    depends_on('zlib', when='@neuron')
    depends_on('mpi', when='@neuron')
    depends_on('cmake', when='@neuron', type='build')
    depends_on('tau', when='+profile')

    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def neurodamus_flags(self, spec):
        reporting_inc = spec['reportinglib'].prefix.include
        reporting_lib = spec['reportinglib'].prefix.lib64
        hdf5_inc = spec['hdf5'].prefix.include
        hdf5_lib = spec['hdf5'].prefix.lib
        zlib_lib = spec['zlib'].prefix.lib

        incflags = '-I%s -I%s' % (reporting_inc, hdf5_inc)
        ldflags = '-L%s -lreportinglib -L%s -lhdf5 -L%s -lz' % (reporting_lib, hdf5_lib, zlib_lib)

        return incflags, ldflags

    def check_install(self):
        special = '%s/special' % self.nrnarchdir
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
            self.create_special(incflags, ldflags, 'modlib')

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
                    # mod2c_core can't compile ri.mod
                    if 'nrntraub/mod/ri.mod' in filepath:
                        continue
                    # neuron already have exp2syn.mod but not coreneuron
                    if 'neuron_mod/exp2syn.mod' in filepath and spec.satisfies('@neuron'):
                        continue
                    if '/neurodamus/lib' in filepath and os.path.basename(filepath) not in neurodamus_modfiles:
                        continue
                    shutil.copy(filepath, path)

    def build_single_exec(self, spec, prefix, modpath):
        with working_dir(prefix):
            incflags, ldflags = self.neurodamus_flags(spec)
            self.create_special(incflags, ldflags, modpath)

    def build_bbp_simtestdata(self, spec, prefix):
        src = '%s/simtestdata' % self.stage.source_path
        dest = '%s/simtestdata' % prefix
        install_tree(src, dest, symlinks=False)
        build_dir = '%s/build' % dest

        with working_dir(build_dir, create=True):
            cmake('..')
            blueconfig = 'circuitBuilding_1000neurons/BlueConfig'
            shutil.copy(blueconfig, '../')

    def install(self, spec, prefix):
        with working_dir(prefix):
            modpath = 'modfiles'
            self.copy_compatible_mod_files(spec, modpath)

            if self.spec.satisfies('@neuron'):
                self.profiling_wrapper_on()
                self.build_single_exec(spec, prefix, modpath)
                self.build_neurodamus(spec, prefix)
                self.build_nrntraub(spec, prefix)
                self.build_dentate(spec, prefix)
                self.build_ringtest(spec, prefix)
                self.build_tqperf(spec, prefix)
                self.build_bbp_simtestdata(spec, prefix)
                self.profiling_wrapper_off()

    def setup_environment(self, spack_env, run_env):
        prefix = self.prefix
        modfiles = '%s/modfiles' % prefix
        run_env.set('NRNPERF_MODFILES', modfiles)
        run_env.set('NRNPERF_HOME', prefix)

        if self.spec.satisfies('@neuron'):
            archdir = self.nrnarchdir
            blueconfig = '%s/simtestdata/BlueConfig' % prefix
            neurodamus_exe = '%s/neurodamus/lib/%s/special' % (prefix, archdir)
            nrntraub_exe = '%s/nrntraub/%s/special' % (prefix, archdir)
            dentate_exe = '%s/reduced_dentate/%s/special' % (prefix, archdir)
            ringtest_exe = '%s/%s/bin/nrniv' % (self.spec['neuron'].prefix, archdir)
            tqperf_exe = '%s/tqperf/%s/special' % (prefix, archdir)
            nrnperf_exe = '%s/%s/special' % (prefix, archdir)
            pythonpath = "%s/tqperf" % prefix

            neurodamus_hoc_path = '%s/neurodamus/lib/hoclib' % prefix
            traub_hoc_path = '%s/nrntraub:%s/nrntraub/hoc' % (prefix, prefix)
            ring_hoc_path = '%s/ringtest' % prefix
            rd_hoc_path = '%s/reduced_dentate:%s/reduced_dentate/templates' % (prefix, prefix)
            tq_hoc_path = '%s/tqperf' % prefix

            run_env.set('BBP_EXE', neurodamus_exe)
            run_env.set('TRAUB_EXE', nrntraub_exe)
            run_env.set('DENTATE_EXE', dentate_exe)
            run_env.set('RINGTEST_EXE', ringtest_exe)
            run_env.set('TQPERF_EXE', tqperf_exe)
            run_env.set('NRNPERF_EXE', nrnperf_exe)

            run_env.set('BLUECONFIG', blueconfig)
            run_env.prepend_path('PYTHONPATH', pythonpath)

            run_env.set('BBP_HOC_PATH', neurodamus_hoc_path)
            run_env.set('TRAUB_HOC_PATH', traub_hoc_path)
            run_env.set('DENTATE_HOC_PATH', rd_hoc_path)
            run_env.set('RINGTEST_HOC_PATH', ring_hoc_path)
            run_env.set('TQPERF_HOC_PATH', tq_hoc_path)

    def setup_dependent_package(self, module, dspec):
        dspec.package.nrnperf_modfiles = '%s/modfiles' % self.prefix
