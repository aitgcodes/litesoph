from litesoph.simulations.esmd import Task
from litesoph.simulations.gpaw import gpaw_template as gp
from litesoph.simulations.nwchem import nwchem_template as nw
from litesoph.simulations.octopus import octopus_template as ot

task_dict = {
    'gpaw' : {
        'ground_state' : gp.GpawGroundState,
        'rt_tddft_delta' : gp.GpawRTLCAOTddftDelta,
        'rt_tddft_laser' : gp.GpawRTLCAOTddftLaser,
        'spectrum' : gp.GpawSpectrum,
        'tcm' : gp.GpawCalTCM,
    },

    'nwchem' : {
        'ground_state' : nw.NwchemGroundState,
        'rt_tddft_delta' : nw.NwchemDeltaKick,
        'rt_tddft_laser' : nw.NwchemGaussianPulse,
        'spectrum' : nw.NwchemSpectrum,
        'tcm' : None,

    },

    'octopus' : {
        'ground_state' : ot.OctGroundState,
        'rt_tddft_delta' : ot.OctTimedependentState,
        'rt_tddft_laser' : ot.OctTimedependentLaser,
        'spectrum' : ot.OctSpectrum,
        'tcm' : None,

    }
}

def get_engine_task(engine: str, task: str, status, directory, lsconfig, user_input) -> Task:

    try:
        task  = task_dict[engine][task](status, directory, lsconfig, user_input)
    except KeyError:
        raise Exception("Task not implemented")

    return task

