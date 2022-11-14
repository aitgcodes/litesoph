from typing import List, Dict, Union
from pathlib import Path
from litesoph.common.task_data import GROUND_STATE, RT_TDDFT, COMPUTE_SPECTRUM
from litesoph.common.workflow_manager import WorkflowManager
from litesoph.common.workflows_data import workflow_types
from litesoph.common.task import TaskSetupError
from litesoph.common.data_sturcture import WorkflowInfo, TaskInfo, factory_task_info

class SpectrumWorkflow(WorkflowManager):

    def __init__(self, 
                project_manager, 
                workflow_info: WorkflowInfo, 
                config: Dict[str, str]) -> None:
        
        
        super().__init__(project_manager,
                        workflow_info,
                        config)

        if not self.tasks:
            self.current_step.insert(0, list(self.steps.keys())[0])
        self.engine_current_tasks = []

    def save_input(self, param):            
        task_infolist = self._get_taskinfo_from_uuid(self.steps[self.current_step[0]])
        for taskinfo in task_infolist:
            taskinfo.param.update(param)
            task_dependencies = self.get_task_dependencies(taskinfo.uuid)
            task = self._get_task(taskinfo, task_dependencies)

            task.create_input()
            task.save_input()
            self.engine_current_tasks.append(task)

    def create_input(self):
        pass
    
    def get_task_dependencies(self, uuid):
        return self._get_taskinfo_from_uuid(self.dependencies_map[uuid])
    
    def build_execution_path():
        pass

    def prepare_for_submission():
        pass
    
    def create_job_script(self):
        pass

    def write_job_script(self):
        pass

    def next():
        pass

    def run_local(self, n=1, cmd='bash'):
        for task in self.engine_current_tasks:
            if task.task_name == COMPUTE_SPECTRUM:
                task.prepare_input()
                np = 1
                cmd = 'bash'
            task.set_submit_local(np)
            task.run_job_local(cmd)

