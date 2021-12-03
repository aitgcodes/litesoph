"""LITESOPH command-line tool."""
import os
import subprocess
import sys


from ase.cli.main import main as ase_main

from gpaw import __version__


commands = [
    ('run', 'litesoph.cli.run')
]

def hook(parser, args):
    parser.add_argument('-P', '--parallel', type=int, metavar='N',
                        help='Run on N CPUs.')
    args, extra = parser.parse_known_args(args)
    if extra:
        assert not args.arguments
        args.arguments = extra

    if args.command == 'python':
        args.traceback = True

    if hasattr(args, 'dry_run'):
        N = int(args.dry_run)
        if N:
            import gpaw
            gpaw.dry_run = N
            import gpaw.mpi as mpi
            mpi.world = mpi.SerialCommunicator()
            mpi.world.size = N

    if args.parallel:
        from gpaw.mpi import have_mpi, world
        if have_mpi and world.size == 1 and args.parallel > 1:
            py = sys.executable
        elif not have_mpi:
            py = 'gpaw-python'
        else:
            py = ''

        if py:
            # Start again in parallel:
            arguments = ['mpiexec',
                         '-np',
                         str(args.parallel),
                         py,
                         '-m',
                         'gpaw'] + sys.argv[1:]

            extra = os.environ.get('GPAW_MPI_OPTIONS')
            if extra:
                arguments[1:1] = extra.split()

            # Use a clean set of environment variables without any MPI stuff:
            p = subprocess.run(arguments, check=not True, env=os.environ)
            sys.exit(p.returncode)

    return args


def main(args=None):
    ase_main('litesoph', 'LITESOPH command-line tool', __version__,
             commands, hook, args)
