"""Generate a human-readable profile schema string from Pydantic models.

The output is injected into LLM system prompts so the model knows
the exact shape of the profile JSON it is expected to produce.
"""
import types
from typing import get_args, get_origin

from backend.routers.profile import (
    ActivityEntry,
    CertificationEntry,
    EducationEntry,
    ExperienceEntry,
    ProfileRequest,
)


def _type_str(annotation) -> str:
    """Convert a Python type annotation to a compact human-readable string.

    Examples
    --------
    str          -> "string"
    int          -> "integer"
    list[str]    -> "string[]"
    str | None   -> "string | null"
    """
    # Handle None / NoneType
    if annotation is type(None):
        return "null"

    # Handle Python 3.10+ union syntax: X | Y (types.UnionType)
    if isinstance(annotation, types.UnionType):
        parts = [_type_str(a) for a in get_args(annotation)]
        return " | ".join(parts)

    # Handle typing.Union (used internally by pydantic for Optional etc.)
    origin = get_origin(annotation)
    if origin is types.UnionType or str(origin) == "typing.Union":
        parts = [_type_str(a) for a in get_args(annotation)]
        return " | ".join(parts)

    # Handle list[X]
    if origin is list:
        inner_args = get_args(annotation)
        inner = _type_str(inner_args[0]) if inner_args else "any"
        return f"{inner}[]"

    # Primitive mappings
    primitives = {
        str: "string",
        int: "integer",
        float: "float",
        bool: "boolean",
    }
    if annotation in primitives:
        return primitives[annotation]

    # Fall back to the class name
    name = getattr(annotation, "__name__", None)
    return name if name else str(annotation)


def _format_model(model_class, indent: int) -> str:
    """Return a multi-line string describing all fields of a Pydantic model."""
    pad = " " * indent
    lines: list[str] = []
    for field_name, field_info in model_class.model_fields.items():
        annotation = field_info.annotation
        origin = getattr(annotation, "__origin__", None)

        # list[SomePydanticModel] → render nested block
        if origin is list:
            inner_args = get_args(annotation)
            inner_type = inner_args[0] if inner_args else None
            if inner_type is not None and hasattr(inner_type, "model_fields"):
                lines.append(f"{pad}{field_name}:")
                lines.append(f"{pad}  [")
                lines.append(_format_model(inner_type, indent + 4))
                lines.append(f"{pad}  ]")
                continue

        type_label = _type_str(annotation)
        lines.append(f"{pad}{field_name}: {type_label}")

    return "\n".join(lines)


def generate_profile_schema() -> str:
    """Return a human-readable schema string for ``ProfileRequest``."""
    lines: list[str] = ["Profile Schema:"]

    for field_name, field_info in ProfileRequest.model_fields.items():
        annotation = field_info.annotation
        origin = getattr(annotation, "__origin__", None)

        # list[SomePydanticModel] → render nested block
        if origin is list:
            inner_args = get_args(annotation)
            inner_type = inner_args[0] if inner_args else None
            if inner_type is not None and hasattr(inner_type, "model_fields"):
                lines.append(f"  {field_name}:")
                lines.append("    [")
                lines.append(_format_model(inner_type, indent=6))
                lines.append("    ]")
                continue

        type_label = _type_str(annotation)
        lines.append(f"  {field_name}: {type_label}")

    return "\n".join(lines)
