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
