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
    """Run calculation with GPAW.

    Types of calculations can be done:

    * Ground State
    * LCAO TDDFT
    

    Examples of the four types of calculations:

        litesoph run -p xc=PBE h2o.xyz
       
    """

    @staticmethod
    def add_arguments(parser):
        ASECLICommand.add_more_arguments(parser)
        parser.add_argument('--dry-run', type=int, default=0,
                            metavar='NCPUS',
                            help='Dry run on NCPUS cpus.')
        parser.add_argument('-w', '--write', help='Write gpw-file.')
        parser.add_argument('-W', '--write-all',
                            help='Write gpw-file with wave functions.')

    @staticmethod
    def run(args):
        runner = LITESOPHRunner()
        runner.parse(args)
        runner.run()
