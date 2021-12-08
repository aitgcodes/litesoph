from ase.cli.run import Runner, str2dict, CLICommand as ASECLICommand

from gpaw import GPAW
from gpaw.mixer import Mixer, MixerSum
from gpaw.occupations import (FermiDirac, MethfesselPaxton,
                              MarzariVanderbilt)
from gpaw import PW


class LITESOPHRunner(Runner):
    def __init__(self):
        Runner.__init__(self)
        self.calculator_name = 'gpaw'

    def parse(self, args):
        args.calculator = 'gpaw'
        print(args)
        return Runner.parse(self, args)

    def set_calculator(self, atoms, name):
        parameter_namespace = {
            'PW': PW,
            'FermiDirac': FermiDirac,
            'MethfesselPaxton': MethfesselPaxton,
            'MarzariVanderbilt': MarzariVanderbilt,
            'Mixer': Mixer,
            'MixerSum': MixerSum}
        parameters = str2dict(self.args.parameters, parameter_namespace)
        txt = parameters.pop('txt', self.get_filename(name, 'txt'))
        atoms.calc = GPAW(txt=txt, **parameters)

    def calculate(self, atoms, name):
        data = Runner.calculate(self, atoms, name)
        if self.args.write:
            atoms.calc.write(self.args.write)
        if self.args.write_all:
            atoms.calc.write(self.args.write_all, 'all')
        return data


class CLICommand:
    """Run calculation with LITESOPH.

    Types of calculations can be done:

       
    """

    @staticmethod
    def add_arguments(parser):
        #ASECLICommand.add_more_arguments(parser)
        add = parser.add_argument
        add('name', nargs='?', default='-',
            help='Read atomic structure from this file.')
        add('-p', '--parameters', default='',
            metavar='key=value,...',
            help='Comma-separated key=value pairs of ' +
            'calculator specific parameters.')
        add('-t', '--tag',
            help='String tag added to filenames.')
        add('--properties', default='efsdMm',
            help='Default value is "efsdMm" meaning calculate energy, ' +
            'forces, stress, dipole moment, total magnetic moment and ' +
            'atomic magnetic moments.')
        add('-f', '--maximum-force', type=float,
            help='Relax internal coordinates.')
        add('--constrain-tags',
            metavar='T1,T2,...',
            help='Constrain atoms with tags T1, T2, ...')
        add('-s', '--maximum-stress', type=float,
            help='Relax unit-cell and internal coordinates.')
        add('-E', '--equation-of-state',
            help='Use "-E 5,2.0" for 5 lattice constants ranging from '
            '-2.0 %% to +2.0 %%.')
        add('--eos-type', default='sjeos', help='Selects the type of eos.')
        add('-o', '--output', help='Write result to file (append mode).')
        add('--modify', metavar='...',
            help='Modify atoms with Python statement.  ' +
            'Example: --modify="atoms.positions[-1,2]+=0.1".')
        add('--after', help='Perform operation after calculation.  ' +
            'Example: --after="atoms.calc.write(...)"')
        add('--dry-run', type=int, default=0,
                            metavar='NCPUS',
                            help='Dry run on NCPUS cpus.')
        add('-w', '--write', help='Write gpw-file.')
        add('-W', '--write-all',
                            help='Write gpw-file with wave functions.')

    @staticmethod
    def run(args):
        runner = LITESOPHRunner()
        runner.parse(args)
        runner.run()

