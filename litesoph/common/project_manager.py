import shutil
from typing import Any, Dict
import uuid
import copy

from pathlib import Path
import os
from litesoph.common.utils import create_dir, PROJECT_DATA_FILE_RELATIVE_PATH, PROJECT_DATA_FILE_NAME, WORKFLOW_DATA_FILE_NAME
from litesoph.common.data_sturcture.data_classes import ProjectInfo, WorkflowInfo
from litesoph.visualization.visualize_geometry import VisualizeGeometry
from litesoph.common.workflow_manager import WorkflowManager
from litesoph.common.workflows_data import predefined_workflow
from litesoph.common.decision_tree import decide_engine

class WorkflowSetupError(Exception):
    """Raised when unable to creating or opening task."""

class ProjectManager:
    """This class is responsible for creating, loading and managing
    all the workflows in the projects.
    
    Parameters
    ----------
    
    ls_manager: 
        LSManager object loaded with a project.
    project_info:
        ProjectInfo to store all the information generated in 
        the project.
    """
    
    def __init__(self, ls_manager, project_info: ProjectInfo) -> None:
        self.ls_manager = ls_manager
        self.project_info = project_info
        self.label = project_info.label
        self.workflow_list = project_info.workflows
        self.project_path = project_info.path
        self.config = project_info.config
        self.current_workflow_info = None
        vis_tools = self.config.get('visualization_tools', None)
        self.visualize = VisualizeGeometry(vis_tools)

        if self.workflow_list:
            self.current_workflow_info = self.workflow_list[-1]
        else:
            self.new_workflow('workflow_1')
        self.save()

    def _create_workflow_info(self, label: str, description: str =''):
        
        current_workflow = self.project_path / label
        try:
            create_dir(current_workflow)
        except Exception as e:
            raise WorkflowSetupError(f'Unable to create New workflow. Error:{e}')

        workflow_info = WorkflowInfo(str(uuid.uuid4()), 
                                        label=label, 
                                        path= current_workflow,
                                        description=description)
        return workflow_info

    def new_workflow(self, label: str, description: str =''):
        """This method creates a new workflow info and saves it in the
        project.
        
        Parameters
        ----------

        label:
            user given name of the workflow
        description:
            description or comments about the workflow.
        """
        
        self.current_workflow_info = self._create_workflow_info(label=label, 
                                                            description=description)
        self.append_workflow(self.current_workflow_info)
        self.save()
    
    def clone_workflow(self, workflow_info_uuid : str,
                            traget_workflow_type: str,
                            branch_point: int, 
                            label: str, 
                            description: str =''):
        
        """This method creates new workflow by clone any workflows 
        in the project into
        
        Parameters
        ----------
        workflow_info_uuid:
                The uuid of the source workflow
        traget_workflow_type:
                The workflow type of the cloned workflow.
        branch_point:
            It's is the block id in the workflow. It is the point upto 
            which workflow is cloned.
        label:
            label of the new cloned workflow
        description:
            description or comments about the cloned workflow."""
        
        
        workflow_info  = self.get_workflow_info(workflow_info_uuid)
        
        if workflow_info.name != traget_workflow_type:
            raise WorkflowSetupError('The traget worrkflow should be same as the parent workflow.')

        workflow_manager = WorkflowManager(self, workflow_info, self.config)

        cloned_workflow_info = self._create_workflow_info(label=label,
                                                        description=description)
        cloned_workflow_info.name = copy.deepcopy(workflow_info.name)
        cloned_workflow_info = workflow_manager.clone(cloned_workflow_info,
                                                            branch_point=branch_point)

        self.append_workflow(cloned_workflow_info)
        self.save()

    def _get_workflow_manager(self, name):
        if name == 'task_mode':
            return WorkflowManager

        workflow_type = predefined_workflow.get(name, None)
        if not workflow_type:
            raise WorkflowSetupError(f'Workflow:{name} not defined.')
        
        return WorkflowManager

    def start_workflow(self, workflow_type: str, param: Dict[str, Any]) -> WorkflowManager:
        """This method instantiates the workflow manager with the workflow_type and
        returns the workflow manager.
        
        Parameters
        ----------
        
        workflow_type:
            The workflow indentifier.
        param:
            parameters."""

        if not self.current_workflow_info:
            raise WorkflowSetupError('Create workflow')

        workflow_manager = self._get_workflow_manager(workflow_type)
        self.current_workflow_info.name = workflow_type 
        if workflow_type == 'task_mode':
            self.current_workflow_info.task_mode = True       
        self.current_workflow_info.param.update(param)
        workflow_manager = workflow_manager(self, self.current_workflow_info, config=self.config)
        return workflow_manager

    def open_workflow(self, workflow_uuid: str) -> WorkflowManager:
        """This method opens already existing and defined workflow."""
        workflow_info = self.get_workflow_info(workflow_uuid)        
        workflow_manager = self._get_workflow_manager(workflow_info.name)       
        workflow_manager = workflow_manager(self, workflow_info, config=self.config)
        self.current_workflow_info = workflow_info
        return workflow_manager 
    
    def get_workflow_info(self, workflow_uuid):
        """returns WorkflowInfo object from the uuid."""
        for workflow in self.workflow_list:
            if workflow.uuid == workflow_uuid:
                return  workflow
        raise ValueError(f"workflow with uuid: {workflow_uuid} doesn't exists.")

    def list(self) -> list:
        """returns list of tuples contain label and uuids of all the workflows
        in the project."""
        workflows = [(workflow.label, workflow.uuid) for workflow in self.workflow_list]
        return workflows
    
    def add_geometry(self, geometry_file):
        geom_path = self.current_workflow_info.path / "coordinate.xyz"
        shutil.copy(geometry_file, geom_path)
        self.current_workflow_info.param.update({'geometry': str(geom_path)})

    def check(self) -> bool:
        geom = self.current_workflow_info.param.get('geometry', None)
        if geom:
            return True
        else:
            return False
            
    def visualize_geometry(self):
        default_geom_file = self.current_workflow_info.path / 'coordinate.xyz'
        geom_file = self.current_workflow_info.param.get('geometry', str(default_geom_file))
        self.visualize.render(geom_file)
    
    def get_summary(self):
        pass

    def save(self):
        file = self.project_path / self.ls_manager.project_data_file_relative_path
        try:
            json_txt = self.project_info.to_json()
        except TypeError:
            raise
        
        with open(file, 'w') as f:
            f.write(json_txt)

    def remove(self, workflow_uuid):
        """This removes a workflow from the project. It will
        also delete the corresponding directory. """
        for workflow in self.workflow_list:
            if workflow.uuid == workflow_uuid:
                shutil.rmtree(str(workflow.path))
                self.workflow_list.remove(workflow)


    def _change_directory(self, path):
        "changes current working directory"
        os.chdir(path)

    def list_available_workflows(self):
        """Returns a list of all the predefined workflow types."""
        return [workflow for workflow in predefined_workflow.keys()]

    def append_workflow(self, workflow_info: WorkflowInfo):
        for workflow in self.workflow_list:
            if workflow.uuid == workflow_info.uuid:
                return
        self.workflow_list.append(workflow_info)

    def get_predefined_workflow(self):
        pass
    
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