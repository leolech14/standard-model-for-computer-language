"""
Plugin System - Universal Module Interface
===========================================

Provides base classes and protocols for Hub-connected modules.

Exports:
    - BasePlugin: Universal interface for all Hub modules
    - ServicePlugin: Modules that provide services
    - EventDrivenPlugin: Modules that react to events
"""

from .base_plugin import BasePlugin, ServicePlugin, EventDrivenPlugin

__all__ = ['BasePlugin', 'ServicePlugin', 'EventDrivenPlugin']
