"""A tiny model registry — how the pipeline discovers available models.

Register each ModelPlugin here (or via an entry point). The orchestrator and the
LLM assistant both read this registry to know what's runnable.
"""
from __future__ import annotations
from .base import ModelPlugin

_REGISTRY: dict[str, ModelPlugin] = {}


def register(model):
    """Register a ModelPlugin. Works as a class decorator or on an instance.

    A class is instantiated once and its singleton stored; the original class is
    returned so `@register` stays transparent.
    """
    inst = model() if isinstance(model, type) else model
    if inst.name in _REGISTRY:
        raise ValueError(f"model '{inst.name}' already registered")
    _REGISTRY[inst.name] = inst
    return model


def get(name: str) -> ModelPlugin:
    return _REGISTRY[name]


def all_models() -> list[ModelPlugin]:
    return list(_REGISTRY.values())


def catalog() -> list[dict]:
    """Machine-readable list the assistant uses to pick models."""
    return [{"name": m.name, "modality": m.modality, "description": m.description}
            for m in _REGISTRY.values()]
