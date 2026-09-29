from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, default=str, separators=(",", ":"))


def sha256(data: Any) -> str:
    if isinstance(data, str):
        payload = data.encode()
    else:
        payload = canonical(data).encode()
    return hashlib.sha256(payload).hexdigest()
