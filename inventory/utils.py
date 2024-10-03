# inventory/utils.py

from django.core.exceptions import PermissionDenied
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def roles_required(required_roles):
    def decorator(func):
        @wraps(func)
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated:
                user_role = getattr(request.user, 'role', None)
                logger.debug(f"User '{request.user.username}' Role: {user_role}")
                logger.debug(f"Allowed Roles for '{func.__name__}': {required_roles}")

                if user_role in required_roles:
                    return func(request, *args, **kwargs)
                else:
                    logger.warning(f"Permission Denied for user '{request.user.username}' with role '{user_role}'")
            else:
                logger.warning(f"Unauthenticated access attempt to '{func.__name__}'")
            raise PermissionDenied
        return wrapped
    return decorator
