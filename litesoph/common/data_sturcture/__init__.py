from litesoph.common.data_sturcture.utils import *
from litesoph.common.data_sturcture.data_classes import *
from litesoph.common.data_sturcture.data_types import *



def factory_task_info(name: str) -> TaskInfo:

    return TaskInfo(str(uuid.uuid4()), name)