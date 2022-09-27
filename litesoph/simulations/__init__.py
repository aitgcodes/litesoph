from distutils.command.sdist import sdist
import shutil
from litesoph.simulations.gpaw.gpaw_task import GpawTask
from litesoph.simulations.nwchem.nwchem_task import NwchemTask
from litesoph.simulations.octopus.octopus_task import OctopusTask
from litesoph.simulations import gpaw as g
from litesoph.simulations import nwchem as n
from litesoph.simulations import octopus as o
from pathlib import Path
import os
from litesoph.config import config_file, config_to_dict, dict_to_config
from litesoph.simulations.project_status import Status
from litesoph.visualization.visualize_geometry import VisualizeGeometry

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

class ProjectSetupError(Exception):
    """Raised when unable to create new project."""

class TaskManager:

    def __init__(self) -> None:
        self.project_list = []
        self.current_task = None
        self.current_project = None
        self.current_project_status = None
        self.task_objects = []
        self.read_lsconfig()
        vis_tools = self.lsconfig.get('visualization_tools', None)
        self.visualize = VisualizeGeometry(vis_tools)

    def read_lsconfig(self):
        self.lsconfig = config_to_dict(config_file)

    def get_task(self, engine: str, task: str,user_input):
        user_input['task'] = task
        directory = self.current_project
        lsconfig = self.lsconfig
        status = self.current_project_status
        if engine == 'nwchem':
            task = NwchemTask(directory, lsconfig, status, **user_input)
        elif engine == 'octopus':
            task = OctopusTask(directory, lsconfig, status, **user_input)
        elif engine == 'gpaw':
            task = GpawTask(directory, lsconfig, status, **user_input)

        self.current_task_list.append(type(task).__name__)
        self.task_objects.append(task)
        return task

    def create_new_project(self, project_path: Path):
        
        try:
            self.create_dir(project_path)
        except:
            raise
        self.init_project(project_path, new_project=True)
    
    def open_existing_project(self, project_path: Path):

        self.init_project(project_path)
    
    def init_project(self, project_path, new_project=False):
        
        self.current_project_data = p_data = {}
        self.current_project = project_path
        if new_project:
            p_data['name'] = project_path.name
            p_data['path'] = str(self.current_project)
            p_data['tasks'] = []
        try:
            self.current_project_status = Status(self.current_project, p_data)
        except Exception:
            p_data = {}
            raise
        self.current_task_list = p_data['tasks']
        self.project_list.append(self.current_project_data)
        self._change_directory(self.current_project)

    def get_previous_engine(self)-> list:
        non_engine_keys = ['name', 'path', 'tasks', 'geometry']
        keys = self.current_project_data.keys()
        for key in keys:
            if key in non_engine_keys:
                continue
            else:
                return key

    def add_geometry(self, geometry_file):
        geom_path = self.current_project / "coordinate.xyz"
        shutil.copy(geometry_file, geom_path)
        # self.current_project_data['geometry'] = str(geom_path)
        self.current_project_status.update('geometry', str(geom_path))

    def check_geometry(self):
        geom = self.current_project_data.get('geometry', None)
        if geom:
            return True
        else:
            return False
            
    def visualize_geometry(self):
        default_geom_file = self.current_project / 'coordinate.xyz'
        geom_file = self.current_project_data.get('geometry', str(default_geom_file))
        self.visualize.render(geom_file)
    
    def get_project_summary(self):
        if not self.current_project:
            return ''
        return summary_of_current_project(self.current_project_data)

    def check_status(self, engine, task, status):

        return  task_dict[engine][task][0](status)

    def _change_directory(self, path):
        "changes current working directory"
        os.chdir(path)

    @staticmethod
    def check_dir_exists(project_path):
        """ check if directory exists. """
        project_path = Path(project_path)
        dir_exists = os.access(project_path, os.F_OK)
        return dir_exists
            

    @staticmethod
    def create_dir(project_path):
        """ Creates project directory. """
        project_path = Path(project_path)
        parent_writeable = os.access(project_path.parent, os.W_OK)

        if not parent_writeable:
            msg = f'Permission denied creating directory: {project_path}'
            raise PermissionError(msg)

        project_path = Path(project_path)
        os.makedirs(project_path)



def summary_of_current_project(project_data: dict):

    state = ["Summary of all the tasks performed."]

    engine_list = list(project_data.keys())
    non_engine = ['name', 'path', 'tasks', 'geometry']

    if engine_list:
        state.append(" ")
        for engine in engine_list:
            if engine in non_engine:
                continue
            state.append(f"Engine: {engine}")

            task_list = project_data[engine].keys()

            if task_list:
                for i, task in  enumerate(task_list):
                    if project_data[engine][task]['done'] == True:
                        state.append(f"     {task}")
                    
                
                state.append(" ")
    else:
        state.append("No tasks have been performed yet.")

    state = "\n".join(state)

    return state