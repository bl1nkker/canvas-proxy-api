import os
import sys
from typing import Optional, Dict, Union

import yaml


def read_config_file(file_name: str) -> Optional[Dict[str, Union[str, Dict]]]:
    """
    Reads configuration from a YAML or .env file.
    """
    config_data = {}
    for syspath in [os.getcwd(), *sys.path]:
        config_file = os.path.join(syspath, file_name)
        if os.path.exists(config_file) and os.path.isfile(config_file):
            # For yaml files
            with open(config_file) as f:
                file_data = yaml.load(f, yaml.FullLoader)
                if isinstance(file_data, dict):
                    config_data.update(file_data)
    return config_data if config_data else None
