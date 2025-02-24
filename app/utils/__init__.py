import os
from os import environ
from pathlib import Path
from threading import RLock
from typing import Type, Callable, Dict, Optional

from .lock import with_lock
from .read_config_file import read_config_file

_config_lock = RLock()
_config_cache: Dict[Type, object] = {}


@with_lock(lock=_config_lock)
def clear_config_cache(type: Optional[Type] = None):
    global _config_cache

    if type is None:
        _config_cache.clear()
    elif type in _config_cache:
        del _config_cache[type]


def generate_get_config_method(
    type: Type, get_config: Callable[[Callable[[str], str], bool], dict]
):
    @with_lock(lock=_config_lock)
    def _method(file: str = "app.yaml", **defaults) -> type:
        if type in _config_cache:
            return _config_cache[type]

        yaml = read_config_file(file)

        def _get_value(key: str):
            for src in [environ, yaml, defaults]:
                value = src.get(key)
                if value is not None:
                    return value

        is_test = _get_value("PYTHON_ENV") == "test"
        config = get_config(_get_value, is_test)
        _config_cache[type] = type(**config)
        return _config_cache[type]

    return _method


def _find_project_dir() -> Optional[str]:
    cwd = Path(os.getcwd())
    while not os.path.exists(os.path.join(str(cwd), "app.yaml")):
        cwd = Path(cwd.parent)
        if cwd == Path("/"):
            return

    return str(cwd)


def replace_known_dirs(p: Optional[str]):
    if p is None:
        return

    project_dir = _find_project_dir()
    if project_dir is None:
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return p.replace("$HOME", str(Path.home())).replace("$PROJECT", project_dir)
