"""
Decorators for easy error handling and recovery
"""

import functools
import time
from typing import Any, Callable, Optional, Dict, Type, Union, List
from .error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
from .recovery_manager import RecoveryManager


def handle_errors(
    category: Er