"""
Decorators for easy error handling and recovery
"""

import functools
import time
from typing import Any, Callable, Optional, Type, Union, List
from .error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
from .recovery_manager import RecoveryManager


def handle_errors(
    category: ErrorCategory,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    component: Optional[str] = None,
    recovery_scenario: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    fallback_value: Any = None,
    suppress_errors: bool = False,
    error_handler: Optional[ErrorHandler] = None,
    recovery_manager: Optional[RecoveryManager] = None,
):
    """
    Decorator for comprehensive error handling with automatic recovery

    Args:
        category: Error category for classification
        severity: Error severity level
        component: Component name (defaults to function name)
        recovery_scenario: Recovery scenario to attempt
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries (seconds)
        fallback_value: Value to return if all retries fail
        suppress_errors: Whether to suppress errors and return fallback
        error_handler: Custom error handler instance
        recovery_manager: Custom recovery manager instance
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name as component if not specified
            comp_name = component or func.__name__

            # Get or create error handler
            handler = error_handler or getattr(wrapper, "_error_handler", None)
            if not handler:
                handler = ErrorHandler()
                wrapper._error_handler = handler

            # Get or create recovery manager
            recovery = recovery_manager or getattr(wrapper, "_recovery_manager", None)
            if not recovery:
                recovery = RecoveryManager()
                wrapper._recovery_manager = recovery

            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_error = e

                    # Create context for error handling
                    context = {
                        "function": func.__name__,
                        "args": args,
                        "kwargs": kwargs,
                        "attempt": attempt + 1,
                        "max_attempts": max_retries + 1,
                    }

                    # Handle the error
                    handler.handle_error(
                        error=e,
                        category=category,
                        severity=severity,
                        component=comp_name,
                        context=context,
                    )

                    # If this is the last attempt, don't retry
                    if attempt >= max_retries:
                        break

                    # Attempt recovery if scenario provided
                    if recovery_scenario:
                        recovery_success = recovery.attempt_recovery(
                            recovery_scenario, context
                        )
                        if recovery_success:
                            print(f"🔄 Recovery successful, retrying {comp_name}")
                        else:
                            print(f"❌ Recovery failed for {comp_name}")

                    # Wait before retry
                    if attempt < max_retries:
                        delay = retry_delay * (2**attempt)  # Exponential backoff
                        time.sleep(delay)

            # All retries failed
            if suppress_errors:
                print(f"⚠️ Suppressing error in {comp_name}, returning fallback value")
                return fallback_value
            else:
                # Re-raise the last error
                raise last_error

        return wrapper

    return decorator


def retry_on_failure(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    exponential_backoff: bool = True,
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
):
    """
    Simple retry decorator for specific exceptions

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Base delay between retries
        exponential_backoff: Whether to use exponential backoff
        exceptions: Exception types to retry on
    """
    if not isinstance(exceptions, (list, tuple)):
        exceptions = [exceptions]

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    # Check if this exception should trigger a retry
                    if not any(isinstance(e, exc_type) for exc_type in exceptions):
                        raise  # Re-raise immediately if not in retry list

                    last_error = e

                    # If this is the last attempt, don't retry
                    if attempt >= max_retries:
                        break

                    # Calculate delay
                    if exponential_backoff:
                        delay = retry_delay * (2**attempt)
                    else:
                        delay = retry_delay

                    print(
                        f"🔄 Retry {attempt + 1}/{max_retries} for {func.__name__} in {delay}s"
                    )
                    time.sleep(delay)

            # All retries failed, re-raise the last error
            raise last_error

        return wrapper

    return decorator


def graceful_degradation(
    fallback_value: Any = None, log_errors: bool = True, component: Optional[str] = None
):
    """
    Decorator for graceful degradation - continues execution with fallback value

    Args:
        fallback_value: Value to return on error
        log_errors: Whether to log errors
        component: Component name for logging
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                comp_name = component or func.__name__

                if log_errors:
                    print(f"⚠️ Graceful degradation in {comp_name}: {e}")

                return fallback_value

        return wrapper

    return decorator


def timeout_handler(
    timeout_seconds: float, fallback_value: Any = None, raise_on_timeout: bool = False
):
    """
    Decorator to handle function timeouts

    Args:
        timeout_seconds: Maximum execution time
        fallback_value: Value to return on timeout
        raise_on_timeout: Whether to raise TimeoutError or return fallback
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_handler_func(signum, frame):
                raise TimeoutError(
                    f"Function {func.__name__} timed out after {timeout_seconds}s"
                )

            # Set up timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler_func)
            signal.alarm(int(timeout_seconds))

            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel timeout
                return result

            except TimeoutError:
                if raise_on_timeout:
                    raise
                else:
                    print(f"⏰ Timeout in {func.__name__}, returning fallback value")
                    return fallback_value

            finally:
                signal.signal(signal.SIGALRM, old_handler)

        return wrapper

    return decorator


def log_errors(
    category: ErrorCategory = ErrorCategory.SYSTEM,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    component: Optional[str] = None,
    include_traceback: bool = True,
):
    """
    Decorator to log errors without affecting function behavior

    Args:
        category: Error category
        severity: Error severity
        component: Component name
        include_traceback: Whether to include traceback in logs
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                comp_name = component or func.__name__

                # Get or create error handler
                handler = getattr(wrapper, "_error_handler", None)
                if not handler:
                    handler = ErrorHandler()
                    wrapper._error_handler = handler

                # Log the error
                handler.handle_error(
                    error=e,
                    category=category,
                    severity=severity,
                    component=comp_name,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:100],  # Truncate long args
                        "kwargs": str(kwargs)[:100],
                    },
                )

                # Re-raise the error
                raise

        return wrapper

    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception,
):
    """
    Circuit breaker pattern decorator

    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time to wait before trying again
        expected_exception: Exception type that triggers circuit breaker
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize circuit breaker state on first call
            if not hasattr(wrapper, "failure_count"):
                wrapper.failure_count = 0
                wrapper.last_failure_time = None
                wrapper.state = "closed"  # closed, open, half-open
            current_time = time.time()

            # Check if circuit is open
            if wrapper.state == "open":
                if current_time - wrapper.last_failure_time < recovery_timeout:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
                else:
                    wrapper.state = "half-open"
                    print(f"🔄 Circuit breaker HALF-OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)

                # Success - reset circuit breaker
                if wrapper.state == "half-open":
                    wrapper.state = "closed"
                    wrapper.failure_count = 0
                    print(f"✅ Circuit breaker CLOSED for {func.__name__}")

                return result

            except expected_exception:
                wrapper.failure_count += 1
                wrapper.last_failure_time = current_time

                # Check if we should open the circuit
                if wrapper.failure_count >= failure_threshold:
                    wrapper.state = "open"
                    print(
                        f"🚨 Circuit breaker OPEN for {func.__name__} after {failure_threshold} failures"
                    )

                raise

        return wrapper

    return decorator


# Convenience decorators for common scenarios


def handle_file_errors(component: Optional[str] = None):
    """Convenience decorator for file I/O error handling"""
    return handle_errors(
        category=ErrorCategory.FILE_IO,
        severity=ErrorSeverity.MEDIUM,
        component=component,
        recovery_scenario="file_not_found",
        max_retries=2,
    )


def handle_validation_errors(component: Optional[str] = None):
    """Convenience decorator for validation error handling"""
    return handle_errors(
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.HIGH,
        component=component,
        recovery_scenario="validation_timeout",
        max_retries=3,
    )


def handle_gui_errors(component: Optional[str] = None):
    """Convenience decorator for GUI error handling"""
    return handle_errors(
        category=ErrorCategory.GUI,
        severity=ErrorSeverity.LOW,
        component=component,
        recovery_scenario="gui_initialization_failed",
        max_retries=1,
        suppress_errors=True,
    )


def handle_training_errors(component: Optional[str] = None):
    """Convenience decorator for training error handling"""
    return handle_errors(
        category=ErrorCategory.TRAINING,
        severity=ErrorSeverity.HIGH,
        component=component,
        recovery_scenario="training_step_failed",
        max_retries=3,
    )
