import io
import os
import tempfile
from contextlib import contextmanager
from typing import Any

from pydantic import ValidationError


def prettify_validation_error(error: ValidationError) -> dict[str, Any]:
    errors = error.errors()

    pretty = {}
    for err in errors:
        path = [str(loc) if isinstance(loc, str) else f"[{loc}]" for loc in err["loc"]]
        key = ".".join(path).replace(".[", "[")
        pretty[key] = err["msg"]

    return pretty


@contextmanager
def write_to_temp_file(stream: io.BufferedReader):
    temp_file_name = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            mode="wb",
            suffix=".jpg",
        ) as temp_file:
            temp_file_name = temp_file.name
        with io.FileIO(temp_file_name, "wb") as file:
            while True:
                chunk = stream.read(1024)
                if not chunk:
                    break
                file.write(chunk)
        yield temp_file_name
    except Exception as e:
        raise e
    finally:
        if temp_file_name is not None:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
