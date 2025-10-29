"""Plugin registry for modular component instantiation."""

from typing import Dict, Type, Any, Callable
from abc import ABC


class Registry:
    """Global component registry."""
    
    _registry: Dict[str, Type] = {}
    _factories: Dict[str, Callable] = {}
    
    @classmethod
    def register(cls, name: str, component_class: Type) -> Type:
        """Register a component class."""
        cls._registry[name] = component_class
        return component_class
    
    @classmethod
    def register_factory(cls, name: str, factory: Callable) -> Callable:
        """Register a factory function for custom instantiation."""
        cls._factories[name] = factory
        return factory
    
    @classmethod
    def get(cls, name: str) -> Type:
        """Get registered component class."""
        if name not in cls._registry:
            raise ValueError(f"Unknown component: {name}")
        return cls._registry[name]
    
    @classmethod
    def create(cls, name: str, **kwargs) -> Any:
        """Create an instance of a registered component."""
        if name in cls._factories:
            return cls._factories[name](**kwargs)
        
        component_class = cls.get(name)
        return component_class(**kwargs)
    
    @classmethod
    def list_components(cls) -> Dict[str, str]:
        """List all registered components."""
        return {
            name: cls_type.__doc__ or cls_type.__name__ 
            for name, cls_type in cls._registry.items()
        }


def register(name: str):
    """Decorator to register a component."""
    def decorator(cls: Type) -> Type:
        Registry.register(name, cls)
        return cls
    return decorator


def register_factory(name: str):
    """Decorator to register a factory function."""
    def decorator(func: Callable) -> Callable:
        Registry.register_factory(name, func)
        return func
    return decorator
