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


class Coreneuron(Package):

    """CoreNEURON is a simplified engine for the NEURON simulator
    optimised for both memory usage and computational speed. Its goal
    is to simulate massive cell networks with minimal memory footprint
    and optimal performance."""

    homepage = "https://github.com/BlueBrain/CoreNeuron"
    url      = "ssh://bbpcode.epfl.ch/sim/coreneuron"

    version('develop', git='ssh://bbpcode.epfl.ch/sim/coreneuron',
            preferred=True)
    version('github', git='https://github.com/BlueBrain/CoreNeuron.git')
    version('hdf', git='ssh://bbpcode.epfl.ch/sim/coreneuron',
            branch='sandbox/kumbhar/nrnh5')

    variant('mpi', default=True,
            description="Enable MPI support")
    variant('neurodamusmod', default=True,
            description="Build only MOD files from Neurodamus")
    variant('report', default=True,
            description="Enable soma/compartment report using ReportingLib")
    variant('tests', default=False,
            description="Enable building tests")

    # mandatory dependencies
    depends_on('mod2c', type='build')
    depends_on('mod2c@github', type='build', when='@github')
    depends_on('cmake@2.8.12:', type='build')
    depends_on('mpi@2.2:', when='+mpi')
    depends_on('nrnh5', when='@hdf')
    depends_on('hdf5', when='@hdf')

    # optional dependencies
    depends_on('neurodamus@develop~compile', when='+neurodamusmod')
    depends_on('reportinglib', when='+report')
    depends_on('boost', when='+tests')

    def get_arch_compile_options(self, spec):
        options = []

        # for bg-q, our cmake is not setup properly
        if 'bgq' in self.spec.architecture:
            if spec.satisfies('+mpi'):
                options.extend(['-DCMAKE_C_COMPILER=%s' % spec['mpi'].mpicc,
                                '-DCMAKE_CXX_COMPILER=%s' % spec['mpi'].mpicxx])
            if spec.satisfies('@hdf'):
                options.extend(['-DENABLE_ZLIB_LINK=ON'])

        return options

    def install(self, spec, prefix):

        build_dir = "spack-build-%s" % spec.version

        with working_dir(build_dir, create=True):

            options = ['-DCMAKE_INSTALL_PREFIX:PATH=%s' % prefix,
                       '-DCOMPILE_LIBRARY_TYPE=STATIC']

            if spec.satisfies('+tests'):
                options.extend(['-DUNIT_TESTS:BOOL=ON',
                                '-DFUNCTIONAL_TESTS:BOOL=ON'])
            else:
                options.extend(['-DUNIT_TESTS:BOOL=OFF',
                                '-DFUNCTIONAL_TESTS:BOOL=OFF'])

            if spec.satisfies('+report'):
                options.extend(['-DENABLE_REPORTINGLIB:BOOL=ON'])

            if spec.satisfies('~hdf5'):
                options.extend(['-DENABLE_HDF5:BOOL=OFF'])

            if spec.satisfies('~mpi'):
                options.extend(['-DENABLE_MPI:BOOL=OFF'])

            mech_set = False
            modlib_dir = ''

            if 'MOD_FILE_DIR' in os.environ:
                modlib_dir = os.environ['MOD_FILE_DIR']
                mech_set = True
                if not os.path.isdir(modlib_dir):
                    raise RuntimeError("MOD_FILE_DIR environment variable set but directory doesn't exist!")

            if spec.satisfies('+neurodamusmod'):
                neurodamus_dir = self.spec['neurodamus'].prefix
                modlib_dir = '%s;%s/lib/modlib' % (modlib_dir, neurodamus_dir)
                modfile_list = '%s/lib/modlib/coreneuron_modlist.txt' % (neurodamus_dir)

                options.extend(['-DADDITIONAL_MECHS=%s' % (modfile_list)])
                mech_set = True

            if mech_set:
                options.extend(['-DADDITIONAL_MECHPATH=%s' % (modlib_dir)])

            options.extend(self.get_arch_compile_options(spec))

            cmake('..', *options)
            make()
            make('install')
