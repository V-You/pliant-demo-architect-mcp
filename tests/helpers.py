from __future__ import annotations

import json
from typing import Any


def unpack_tool_result(result: Any) -> Any:
    structured = getattr(result, "structured_content", None)
    if structured not in (None, {}):
        return structured

    content = getattr(result, "content", None) or []
    for item in content:
        item_type = getattr(item, "type", None)
        if item_type == "text":
            text = getattr(item, "text", "")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

    return result
