import json
from datetime import datetime

import pytest

from learn_anything.course_platform.adapters.json_serializers import (
    DTOJSONEncoder,
    dto_obj_hook,
)


def test_dto_json_encoder_datetime():
    s = json.dumps({"t": datetime(2025, 1, 15, 12, 0, 0)}, cls=DTOJSONEncoder)
    assert "2025" in s


def test_dto_obj_hook_passthrough():
    d = {"a": 1, "b": 2}
    assert dto_obj_hook(d) == d
