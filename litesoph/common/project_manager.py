import shutil
from typing import Any, Dict
import uuid

from pathlib import Path
import os
from litesoph.common.utils import create_dir, PROJECT_DATA_FILE_RELATIVE_PATH, PROJECT_DATA_FILE_NAME, WORKFLOW_DATA_FILE_NAME
from litesoph.common.data_sturcture.data_classes import ProjectInfo, WorkflowInfo
from litesoph.visualization.visualize_geometry import VisualizeGeometry
from litesoph.common.workflow_manager import WorkflowManager, factory_task_info
from litesoph.common.workflows_data import predefined_workflow

class WorkflowSetupError(Exception):
    """Raised when unable to creating or opening task."""

class ProjectManager:
    
    workflow_data_file_name = '.workflow.json'

    def __init__(self, ls_manager, project_info: ProjectInfo) -> None:
        self.ls_manager = ls_manager
        self.project_info = project_info
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

    def new_workflow(self, label: str):
        
        current_workflow = self.project_path / label
        try:
            create_dir(current_workflow)
        except Exception as e:
            raise WorkflowSetupError(f'Unable to create New workflow. Error:{e}')

        self.current_workflow_info = WorkflowInfo(str(uuid.uuid4()), label=label, path= current_workflow)
        self.append_workflow(self.current_workflow_info)
        self.save()
    

    def start_workflow(self, workflow_type: str, param: Dict[str, Any]) -> WorkflowManager:

        if not self.current_workflow_info:
            raise WorkflowSetupError('Create workflow')

        # if workflow_type in workflow_types.keys():
        #     workflow_types[workflow_type](self.current_workflow_info)

        elif workflow_type == "user_defined":
            self.current_workflow_info.name = workflow_type
            self.current_workflow_info.user_defined = True
            self.current_workflow_info.steps.update({workflow_type: []})
            
        else:
            raise WorkflowSetupError(f'workflow:{workflow_type} is not Implemented.')

        engine = param.get('engine', None)
        if engine and (engine != 'auto-mode'):
            self.current_workflow_info.engine = engine

        self.current_workflow_info.param.update(param)
        workflow_manager = WorkflowManager(self, self.current_workflow_info, config=self.config)
        return workflow_manager

    def open_workflow(self, uuid) -> WorkflowManager:
        
        for workflow in self.workflow_list:
            if workflow.uuid == uuid:
                self.current_workflow_info = workflow        
                workflow_manager = WorkflowManager(self, workflow, config=self.config)
                return workflow_manager
            else:
                continue
        raise WorkflowSetupError("Workflow with uuid:{uuid} doest exists.")

    def list(self) -> list:
        workflows = [[workflow.label, workflow.uuid] for workflow in self.workflow_list]
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
        with open(file, 'w') as f:
            self.project_info.save(f)

    def remove(self):
        pass

    def _change_directory(self, path):
        "changes current working directory"
        os.chdir(path)

    def list_available_workflows(self):
        return [workflow for workflow in predefined_workflow.keys()]

    def append_workflow(self, workflow_info: WorkflowInfo):
        for workflow in self.workflow_list:
            if workflow.uuid == workflow_info.uuid:
                return
        self.workflow_list.append(workflow_info)

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