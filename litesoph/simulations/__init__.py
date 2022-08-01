from litesoph.simulations.esmd import Task
from litesoph.simulations.gpaw import gpaw_template as gp
from litesoph.simulations.nwchem.nwchem_task import NwchemTask
from litesoph.simulations.octopus.octopus_task import OctopusTask
from litesoph.simulations.octopus import octopus_template as ot
from litesoph.simulations import gpaw as g
from litesoph.simulations import nwchem as n
from litesoph.simulations import octopus as o


task_dict = {
    'gpaw' : {
        'ground_state' : [gp.GpawGroundState, g.pre_condition_ground_state],
        'rt_tddft_delta' : [gp.GpawRTLCAOTddftDelta, g.pre_condition_rt_tddft_delta],
        'rt_tddft_laser' : [gp.GpawRTLCAOTddftLaser,g.pre_condition_rt_tddft_laser],
        'spectrum' : [gp.GpawSpectrum,g.pre_condition_spectrum],
        'tcm' : [gp.GpawCalTCM,g.pre_condition_tcm]
    },

    'nwchem' : {
        'ground_state' : [NwchemTask, n.pre_condition_ground_state],
        'rt_tddft_delta' : [NwchemTask,n.pre_condition_rt_tddft_delta],
        'rt_tddft_laser' :[ NwchemTask,n.pre_condition_rt_tddft_laser],
        'spectrum' : [NwchemTask,n.pre_condition_spectrum],
        'tcm' : [None, n.pre_condition_tcm]
    },

    'octopus' : {
        'ground_state' : [OctopusTask, o.pre_condition_ground_state],
        'rt_tddft_delta' : [OctopusTask, o.pre_condition_rt_tddft_delta],
        'rt_tddft_laser' : [OctopusTask, o.pre_condition_rt_tddft_laser],
        'spectrum' : [OctopusTask, o.pre_condition_spectrum],
        'tcm' : [ot.OctKSD, o.pre_condition_tcm]

    }
}

def get_engine_task(engine: str, task: str, status, directory, lsconfig, user_input) -> Task:

    if engine == 'nwchem':
        return NwchemTask(directory, lsconfig, status, **user_input)
    elif engine == 'octopus' and task in ['ground_state','rt_tddft_delta','rt_tddft_laser','spectrum']:
        return OctopusTask(directory, lsconfig, status, **user_input)

    try:
        task  = task_dict[engine][task][0](status, directory, lsconfig, user_input)
    except KeyError:
        raise Exception("Task not implemented")

    return task


def check_task_pre_conditon(engine, task, status):

    return  task_dict[engine][task][1](status)