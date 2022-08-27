from litesoph.simulations.gpaw.gpaw_task import GpawTask
from litesoph.simulations.nwchem.nwchem_task import NwchemTask
from litesoph.simulations.octopus.octopus_task import OctopusTask
from litesoph.simulations import gpaw as g
from litesoph.simulations import nwchem as n
from litesoph.simulations import octopus as o


task_dict = {
    'gpaw' : {
        'ground_state' : [g.pre_condition_ground_state],
        'rt_tddft_delta' : [g.pre_condition_rt_tddft_delta],
        'rt_tddft_laser' : [g.pre_condition_rt_tddft_laser],
        'spectrum' : [g.pre_condition_spectrum],
        'tcm' : [g.pre_condition_tcm]
    },

    'nwchem' : {
        'ground_state' : [n.pre_condition_ground_state],
        'rt_tddft_delta' : [n.pre_condition_rt_tddft_delta],
        'rt_tddft_laser' :[n.pre_condition_rt_tddft_laser],
        'spectrum' : [n.pre_condition_spectrum],
        'tcm' : [n.pre_condition_tcm],
        'mo_population' : [n.pre_condition_spectrum]
    },

    'octopus' : {
        'ground_state' : [o.pre_condition_ground_state],
        'rt_tddft_delta' : [o.pre_condition_rt_tddft_delta],
        'rt_tddft_laser' : [o.pre_condition_rt_tddft_laser],
        'spectrum' : [o.pre_condition_spectrum],
        'tcm' : [o.pre_condition_tcm]

    }
}

class TaskManager:

    def __init__(self) -> None:
        self.tasks = []

    def get_task(self, engine: str, task: str, status, directory, lsconfig, user_input):
        user_input['task'] = task
        if engine == 'nwchem':
            task = NwchemTask(directory, lsconfig, status, **user_input)
        elif engine == 'octopus':
            task = OctopusTask(directory, lsconfig, status, **user_input)
        elif engine == 'gpaw':
            task = GpawTask(directory, lsconfig, status, **user_input)

        self.tasks.append(task)
        return task

    def check_status(self, engine, task, status):

        return  task_dict[engine][task][0](status)

    