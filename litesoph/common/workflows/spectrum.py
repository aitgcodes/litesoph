from typing import List, Dict, Union
from pathlib import Path
from litesoph.common.task_data import TaskTypes as tt
from litesoph.common.workflow_manager import WorkflowManager
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

    def get_task_dependencies(self,):
        denpendices_uuid = self.dependencies_map.get(self.current_task_info.uuid)
        if denpendices_uuid is None:
            return []
        elif isinstance(denpendices_uuid ,str):
            return [self.tasks.get(denpendices_uuid)]
        elif isinstance(denpendices_uuid, list):
            return [self.tasks.get(task_uuid) for task_uuid in denpendices_uuid]

    def next(self) -> TaskInfo:
        
        self.save()

        if not self.current_step:
            container = self.containers[0]
            self.current_step.insert(0, 0)
            task_id = container.task_uuid
        else:
            container = self.containers[self.current_step[0]]
            if container.next is None:
                raise TaskSetupError('No more tasks in the workflow.')
            task_id = container.next
            self.current_step[0] =+ 1
            container  = self.containers[self.current_step[0]]
        self.current_task_info = self.tasks.get(task_id)
        if self.engine:
            self.current_task_info.engine = self.engine
        self.current_task_info.path = self.directory
        return self.current_task_info


