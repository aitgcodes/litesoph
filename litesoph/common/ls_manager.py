import shutil
from pathlib import Path
import os
from typing import List, Union
import uuid
import json

from litesoph.common.utils import (create_dir, PROJECT_DATA_FILE_NAME,
                                    PROJECT_DATA_FILE_RELATIVE_PATH,
                                    PROJECT_INFO_DIR_NAME)
from litesoph.config import config_file, config_to_dict, dict_to_config
from litesoph.common.data_sturcture.data_classes import ProjectInfo
from litesoph.common.project_manager import ProjectManager


class ProjectSetupError(Exception):
    """Raised when unable to create new project."""


class LSManager:
    """This is the main interface to the litesoph backend.
    This class is responsible for creating and managing all the projects in 
    the litesoph. All the data generated from the project is stored in the 
    project_info which is serialized into json format and written to the project_data file
    in the .litesoph directory, which is in the project directory."""

    def __init__(self) -> None:
        self.project_data_file_relative_path = PROJECT_DATA_FILE_RELATIVE_PATH
        self.project_info_dir_name = PROJECT_INFO_DIR_NAME
        self.current_project = None
        self.current_project_status = None
        self.project_list = []
        self.current_task = None
        self.task_objects = []
        self.read_config()

    def read_config(self):
        """ Reads the lsconfig file and converts it into dict."""
        self.config = config_to_dict(config_file)

    def new_project(self, name: str, path: Union[str, Path], description:str='') -> ProjectManager:
        """Creates Project directory  and instantiates ProjectInfo and project manager
         then return project manager. 
         
        parameters
        ----------
        name: 
            name of the project.
        path:
            path of the project directory.
        description:
            description of the project.
            
        Returns
        -------
            ProjectManager object."""

        project_path = Path(path)

        if not project_path.exists():
            raise ProjectSetupError(f"Path:{str(project_path)} doesn't exists.")
        
        project_path = project_path / name

        try:
            create_dir(project_path)
            info_dir = project_path / self.project_info_dir_name
            create_dir(info_dir)
        except Exception as e:
            raise ProjectSetupError(f'Project: {str(project_path)}. Unable to create directory. Error: {e}')
        
        project_info = ProjectInfo(str(uuid.uuid4()), label= name, path= project_path,
                                    description= description, config= self.config)
        project_data_file = project_path / self.project_data_file_relative_path

        # with open(project_data_file, 'w+') as f:
        #     project_info.save(f)

        self.project_manager = ProjectManager(self, project_info)
        self.append_project(project_info)
        return self.project_manager

    
    def open_project(self, path: Union[str, Path]) -> ProjectManager:
        """Opens a litesoph project.
        
        parameters
        ----------

        path:
            path of the project directory

        Returns
        -------
            ProjectManager object.
        """
        project_path = Path(path)
        project_data_file = project_path / self.project_data_file_relative_path
        if not project_data_file.exists():
            raise ProjectSetupError(f'Project:{str(project_path)} does not exists.')

        with open(project_data_file, 'r') as f:
            try:
                project_data = json.load(f)
            except Exception as e:
                raise ProjectSetupError(f'Project:{str(project_path)}. Unable to read project data from Json. Error:{e}')
        
        try:
            project_info = ProjectInfo.from_dict(project_data)        
        except Exception as e:
            raise ProjectSetupError(f'Project:{str(project_path)}. Unable to load project data. Error:{e}')
        else:
            project_info.config.update(self.config)
            self.project_manager = ProjectManager(self, project_info)
            self.append_project(project_info)
            return self.project_manager

    def list(self):
        pass

    def get_summary(self, name: str) -> str:
        pass
    
    def remove(self):
        pass

    def save(self):
        if hasattr(self, 'project_manager'):
            self.project_manager.save()
        # for project in self.project_list:
        #     file = project.path / self.project_data_file_relative_path
        #     with open(file, 'w') as f:
        #         project.save(f)

    def get_project_summary(self):
        return ' '
        if not self.current_project:
            return ''
        return summary_of_current_project(self.current_project_data)

    def append_project(self, project_info: ProjectInfo):
        for project in self.project_list:
            if project.uuid ==  project_info.uuid:
                return
        self.project_list.append(project_info)


    def _change_directory(self, path):
        "changes current working directory"
        os.chdir(path)


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