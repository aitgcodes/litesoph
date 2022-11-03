import json
from dataclasses import is_dataclass
from pathlib import Path
import os
import uuid


class WorkflowInfoEncoder(json.JSONEncoder):

    def default(self, obj):
        
        if is_dataclass(obj):
            return obj.__dict__

        if isinstance(obj, Path):
            return os.fspath(obj)
             
        return json.JSONEncoder.default(self, obj)

