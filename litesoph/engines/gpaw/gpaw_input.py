import copy
from litesoph.common.task_data import TaskTypes as tt
import numpy as np
default_param =  {
        'geometry' : 'coordinate.xyz',
        'mode': 'fd',
        'xc': 'LDA',
        'occupations': None,
        'poissonsolver': None,
        'h': None,  # Angstrom
        'gpts': None,
        'kpts': [(0.0, 0.0, 0.0)],
        'extra_states': 0,
        'charge': 0,
        'setups': {},
        'basis': {},
        'spinpol': None,
        'filter': None,
        'smearing' : None,
        'mixing': None,
        'eigensolver': None,
        'background_charge': None,
        'experimental': {'reuse_wfs_method': 'paw',
                         'niter_fixdensity': 0,
                         'magmoms': None,
                         'soc': None,
                         'kpt_refine': None},
        'external': None,
        'random': False,
        'hund': False,
        'maxiter': 333,
        'idiotproof': True,
        'symmetry': {'point_group': False},
        'convergence': {'energy': 0.0005,  # eV / electron
                        'density': 1.0e-4,
                        'eigenstates': 4.0e-8,  # eV^2
                        'bands': 'occupied'},  # eV / Ang
        'verbose': 0,
        'fixdensity': False,  # deprecated
        'dtype': None}  # deprecated


gs_template = ("""
from ase.io import read, write
from gpaw import GPAW, Mixer
from numpy import inf

# Molecule or nanostructure
atoms = read('{geometry}')
""",

# Use when Box Dimensions are provided
"""
atoms.set_cell(({box_length_x}, {box_length_y}, {box_length_z}))
atoms.center()
""",

# Else this code
"atoms.center(vacuum={vacuum})\n",

"""
#This initial_calc is just to compute the no. of electrons. The gs and td will take the params inputted by the user.
initial_calc = GPAW(mode='lcao', xc='PBE', txt='no_of_electrons.out')
atoms.set_calculator(initial_calc)
atoms.get_potential_energy()

occupied_bands = initial_calc.get_number_of_electrons() / 2  # Non-spin-polarized
occupied_bands = int(occupied_bands)
unoccupied_bands = {extra_states}
total_bands = occupied_bands + unoccupied_bands

#Ground-state calculation
calc = GPAW(
    mode='{mode}',
    xc='{xc}',
    occupations = {occupations},
    h={h},  # Angstrom
    gpts={gpts},
    kpts={kpts},
    nbands= total_bands,
    charge= {charge},
    setups= {setups},
    basis={basis},
    spinpol= {spinpol},
    filter={filter},
    mixer=Mixer(beta = {mixing}),
    hund={hund},
    maxiter={maxiter},
    symmetry={symmetry},  
    convergence={convergence},
    txt='{txt_out}')
atoms.calc = calc
energy = atoms.get_potential_energy()
calc.write('{gpw_out}', mode='all')
""")

gs_template_with_box_dim = gs_template[0] + gs_template[1] + gs_template[3]
gs_template = gs_template[0] + gs_template[2] + gs_template[3]

def formate_gs(kwargs):
    
    gs_dict = copy.deepcopy(default_param)
    gs_dict.update(kwargs)
    if gs_dict.get('box_dim', None):
        template = copy.deepcopy(gs_template_with_box_dim)
    else:
        template = copy.deepcopy(gs_template)
    restart = kwargs.get('restart', False)

    if restart:
        tlines = template.splitlines()
        tlines.insert(11, "restart ='{gpw_out}',")
        template = """\n""".join(tlines)

    template = template.format(**kwargs)
    return template

delta_kick_template = """ 
from gpaw.lcaotddft import LCAOTDDFT
import numpy as np

td_calc = LCAOTDDFT(filename='{gfilename}',txt='{txt_out}')

td_calc.absorption_kick({absorption_kick})
# Propagate"
td_calc.propagate{propagate}
td_calc.write('{gpw_out}', mode='all')
"""

external_field_template = """ 
import numpy as np
from ase.units import Hartree, Bohr
from gpaw.lcaotddft import LCAOTDDFT

td_calc = LCAOTDDFT(filename='{gfilename}',
                    td_potential=td_potential,
                    txt='{txt_out}')

# Propagate"
td_calc.propagate{propagate}
# Save the state for restarting later"
td_calc.write('{gpw_out}', mode='all')
"""

mask_external_field_template = """
import numpy as np
from ase.units import Hartree, Bohr
from gpaw.lcaotddft.restartfilewriter import RestartFileWriter
from litesoph.pre_processing.gpaw.external_mask import MaskedElectricField
from gpaw.lcaotddft import LCAOTDDFT
from litesoph.pre_processing.gpaw.dipolemomentwriter_mask import DipoleMomentWriter
from gpaw.lcaotddft.laser import GaussianPulse
pulse = GaussianPulse({strength},{time0},{frequency},{sigma}, 'sin')
mask = {mask}
ext = MaskedElectricField(Hartree / Bohr,{polarization}, mask=mask )
td_potential = {{'ext': ext, 'laser': pulse}}
td_calc = LCAOTDDFT(filename='{gfilename}',
                    td_potential=td_potential,
                    txt='{txt_out}')
# Propagate"
td_calc.propagate{propagate}
# Save the state for restarting later"
td_calc.write('{gpw_out}', mode='all')
    """

dm2spec="""
from gpaw.tddft.spectrum import photoabsorption_spectrum
photoabsorption_spectrum('{dm_file}', '{spectrum_file}',folding='{folding}', width={width},e_min={e_min}, e_max={e_max}, delta_e={delta_e})
"""
mo_population ="""
from gpaw import GPAW
from gpaw.lcaotddft import LCAOTDDFT
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.lcaotddft.densitymatrix import DensityMatrix
from litesoph.post_processing.gpaw.mopopulationwriter import MoPopulationWriter

calc = GPAW('{gfilename}', txt=None).fixed_density(nbands='nao', txt='unocc.out')
calc.write('unocc.gpw', mode='all')

td_calc = LCAOTDDFT('unocc.gpw', txt=None)

dmat = DensityMatrix(td_calc)
ksd = KohnShamDecomposition(td_calc)
ksd.initialize(td_calc)
MoPopulationWriter(td_calc, dmat, ksd, filename='{mopop_file}')
# Replay the propagation
td_calc.replay(name='{wfile}', update='none')

"""
tcm_temp = """
from gpaw.lcaotddft import LCAOTDDFT
from gpaw.lcaotddft.frequencydensitymatrix import FrequencyDensityMatrix
from gpaw.tddft.folding import frequencies
import numpy as np
from matplotlib import pyplot as plt
from gpaw import GPAW
from gpaw.tddft.units import au_to_eV
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.lcaotddft.densitymatrix import DensityMatrix
from gpaw.lcaotddft.frequencydensitymatrix import FrequencyDensityMatrix
from gpaw.lcaotddft.tcm import TCMPlotter

# Read the ground-state file
td_calc = LCAOTDDFT('{gfilename}', txt=None)

frequency_list = {frequency_list}

# Attach analysis tools
dmat = DensityMatrix(td_calc)
freqs = frequencies(frequency_list, 'Gauss', 0.1)
fdm = FrequencyDensityMatrix(td_calc, dmat, frequencies=freqs)

# Replay the propagation
td_calc.replay(name='{wfile}', update='none')

# Store the density matrix
fdm.write('fdm.ulm')


# Calculate ground state with full unoccupied space
calc = GPAW('{gfilename}', txt=None).fixed_density(nbands='nao', txt='unocc.out')
calc.write('unocc.gpw', mode='all')

# Construct KS electron-hole basis
ksd = KohnShamDecomposition(calc)
ksd.initialize(calc)
ksd.write('ksd.ulm')

# Load the objects
calc = GPAW('unocc.gpw', txt=None)
ksd = KohnShamDecomposition(calc, 'ksd.ulm')
dmat = DensityMatrix(calc)
fdm = FrequencyDensityMatrix(calc, dmat, 'fdm.ulm')

plt.figure(figsize=(8, 8))


def do(w):
    # Select the frequency and the density matrix
    rho_uMM = fdm.FReDrho_wuMM[w]
    freq = fdm.freq_w[w]
    frequency = freq.freq * au_to_eV
    print(f'Frequency: {{frequency:.2f}} eV')
    print(f'Folding: {{freq.folding}}')

    # Transform the LCAO density matrix to KS basis
    rho_up = ksd.transform(rho_uMM)

    # Photoabsorption decomposition
    dmrho_vp = ksd.get_dipole_moment_contributions(rho_up)
    weight_p = 2 * freq.freq / np.pi * dmrho_vp[0].imag / au_to_eV * 1e5
    print(f'Total absorption: {{np.sum(weight_p):.2f}} eV^-1')

    # Print contributions as a table
    table = ksd.get_contributions_table(weight_p, minweight=0.1)
    print(table)
    with open(f'table_{{frequency:.2f}}.txt', 'w') as f:
        f.write(f'Frequency: {{frequency:.2f}} eV\\n')
        f.write(f'Folding: {{freq.folding}}\\n')
        f.write(f'Total absorption: {{np.sum(weight_p):.2f}} eV^-1\\n')
        f.write(table)

    # Plot the decomposition as a TCM
    de = 0.01
    energy_o = np.arange(-{axis_limit:.2f}, 0.1 + 1e-6, de)
    energy_u = np.arange(-0.1, {axis_limit:.2f} + 1e-6, de)
    plt.clf()
    plotter = TCMPlotter(ksd, energy_o, energy_u, sigma=0.1)
    plotter.plot_TCM(weight_p)
    plotter.plot_DOS(fill={{'color': '0.8'}}, line={{'color': 'k'}})
    plotter.plot_TCM_diagonal(freq.freq * au_to_eV, color='k')
    plotter.set_title(f'Photoabsorption TCM at {{frequency:.2f}} eV')

    # Check that TCM integrates to correct absorption
    tcm_ou = ksd.get_TCM(weight_p, ksd.get_eig_n()[0],
                         energy_o, energy_u, sigma=0.1)
    print(f'TCM absorption: {{np.sum(tcm_ou) * de ** 2:.2f}} eV^-1')

    # Save the plot
    plt.savefig(f'tcm_{{frequency:.2f}}.png')

def run(frequency_list):
    for i, item in enumerate(frequency_list):
        do(i)
run(frequency_list)
"""

task_map = {
    tt.GROUND_STATE: gs_template,
    tt.RT_TDDFT :{'delta': delta_kick_template,
                    'laser': external_field_template},
    tt.COMPUTE_SPECTRUM : dm2spec,
    tt.TCM : tcm_temp,
    tt.MO_POPULATION: mo_population
}

def generate_laser_text(lasers):
    eps = 1e-6 #lower threshold for time origin, switches to Delta Pulse after that
    lines = [
        "from gpaw.lcaotddft.laser import GaussianPulse",
        "from gpaw.external import ConstantElectricField"
    ]
    masked_import_lines = [
        "from litesoph.pre_processing.gpaw.external_mask import MaskedElectricField",
        "from litesoph.pre_processing.gpaw.dipolemomentwriter_mask import DipoleMomentWriter"
    ]
    td_line = ['td_potential = ', '[']
    mask_list_line = ['masks = [']
    len_masks = 0
    for i, laser in enumerate(lasers):

        try:
            # This try block is for future when implementing different type lasers
            laser['sigma']
            sigma_freq = 1/np.maximum(laser['sigma'],eps)
        except:
            pass
        if laser['type'] == 'gaussian':
            import_str = "from gpaw.lcaotddft.laser import GaussianPulse"
            lines.append(f"pulse_{str(i)} = GaussianPulse({laser['strength']},{laser['time0']},{laser['frequency']},{sigma_freq}, 'sin')")
        elif laser['type'] == 'delta':
            import_str = "from litesoph.pre_processing.laser_design import DeltaPulse"
            lines.append(f"pulse_{str(i)} = DeltaPulse({laser['strength']},{round(laser['time0'])})")

        add_import_line(lines, import_str)
        
        # mask dict for each laser
        
        if laser.get('mask', None) is None:
            lines.append(f"ext_{str(i)} = ConstantElectricField(Hartree / Bohr,{laser['polarization']} )")
        else:
            lines.append(f"mask_{str(i)} = {laser['mask']}")
            len_masks += 1
            for line in masked_import_lines:
                add_import_line(lines, line)
            # replacing ConstantElectricField with MaskedElectricField
            lines.append(f"ext_{str(i)} = MaskedElectricField(Hartree / Bohr,{laser['polarization']}, mask = mask_{str(i)} )")
            mask_list_line.append(f"ext_{str(i)}.mask,")

        td_line.append(f"{{'ext': ext_{str(i)}, 'laser': pulse_{str(i)}}},")
        
    mask_list_line.append(']')
    mask_list_line = ''.join(mask_list_line)
    td_line.append(']')
    td_line = ''.join(td_line)

    lines.append(mask_list_line)
    lines.append(td_line)

    return lines, len_masks

def add_import_line(lines, import_str):
    if import_str not in lines:
        lines.insert(0, import_str)

def add_import_line(lines, import_str):
    if import_str not in lines:
        lines.insert(0, import_str)

def assemable_rt(**kwargs):
    tools = kwargs.pop('analysis_tools', None)
    lasers = kwargs.pop('laser', None)
    len_masks = 0
    restart = kwargs.get('restart', False)

    if lasers is not None:        
        # mask as a key in laser dictionary
        template = external_field_template.format(**kwargs) 
        lines = template.splitlines()
        if restart:
            lines.pop(6)
        else:
            lines[4:4] = generate_laser_text(lasers)[0]
            len_masks = generate_laser_text(lasers)[1]
        template = '\n'.join(lines)
 
    else:   
        template = delta_kick_template.format(**kwargs)
        if restart:
            lines = template.splitlines()
            lines[6] = ''
            template = '\n'.join(lines)

    tlines = template.splitlines()
    
    tlines.insert(0, "from gpaw.lcaotddft.restartfilewriter import RestartFileWriter")
    tlines.insert(-5, f"RestartFileWriter(td_calc, '{kwargs.get('gpw_out')}')")

    if 'dipole' in tools:
        dm_files = kwargs.get('dm_files')
        num_dm_files = len(dm_files)

        if (num_dm_files == len_masks+1):
            if len_masks > 0:                
                tlines.insert(-5, f"DipoleMomentWriter(td_calc, '{dm_files[0]}', mask=None, interval={kwargs.get('output_freq', 1)})")
                for i in range(len_masks):             
                    tlines.insert(-5, f"DipoleMomentWriter(td_calc,'{dm_files[i+1]}', mask=masks[{str(i)}], interval={kwargs.get('output_freq', 1)})")
            else:
                tlines.insert(0, 'from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter')
                tlines.insert(-5, f"DipoleMomentWriter(td_calc, '{dm_files[0]}', interval={kwargs.get('output_freq', 1)})")
        
    if "wavefunction" in tools:  
        tlines.insert(0, "from gpaw.lcaotddft.wfwriter import WaveFunctionWriter")
        tlines.insert(-5, f"WaveFunctionWriter(td_calc, '{kwargs.get('wfile', 'wf.ulm')}', interval={kwargs.get('output_freq', 1)})")
        
    if 'mo_population' in tools:
        tlines.insert(0, 'from gpaw.lcaotddft.densitymatrix import DensityMatrix')
        tlines.insert(0, 'from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition')
        tlines.insert(0, 'from litesoph.engines.gpaw.mopopulationwriter import MoPopulationWriter')
        tlines.insert(-5, "dmat = DensityMatrix(td_calc)")
        tlines.insert(-5, "ksd = KohnShamDecomposition(td_calc)")
        tlines.insert(-5, "ksd.initialize(td_calc)")
        tlines.insert(-5,  f"MoPopulationWriter(td_calc, dmat, ksd, filename='{kwargs.get('mopop_file', 'mo_population.dat')}', interval={kwargs.get('output_freq', 1)})")
    
    template = """\n""".join(tlines)
    
    return template

def gpaw_create_input(**kwargs):
    task_name = kwargs.pop('task', tt.GROUND_STATE)

    if tt.RT_TDDFT == task_name:
        return assemable_rt(**kwargs) 

    if tt.GROUND_STATE == task_name:
        return formate_gs(kwargs)
    
    template = task_map.get(task_name)
    template = template.format(**kwargs)
    return template


