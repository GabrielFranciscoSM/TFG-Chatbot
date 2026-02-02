"""
Utility functions for the backend service.
"""

import re

# Patterns for test users that should be filtered from production views
# These match users created by tests (integration, infrastructure, unit)
TEST_USER_PATTERNS = [
    r"^testuser_",  # testuser_<uuid> from infrastructure tests
    r"^integration_user_",  # integration_user_<uuid> from integration tests
    r"^test_",  # test_<something> patterns
]

# Compiled regex for efficiency
_TEST_USER_REGEX = re.compile("|".join(TEST_USER_PATTERNS))


def is_test_user(username: str) -> bool:
    """
    Check if a username matches test user patterns.

    Args:
        username: The username to check

    Returns:
        True if the username matches a test user pattern
    """
    return bool(_TEST_USER_REGEX.match(username))


def get_test_user_filter() -> dict:
    """
    Get a MongoDB filter to exclude test users.

    Returns a filter that can be combined with other query conditions
    using MongoDB's $and operator or merged into existing queries.

    Returns:
        MongoDB filter dict excluding test users

    Example:
        >>> filter = {"role": "student", **get_test_user_filter()}
        >>> # Or with $and:
        >>> filter = {"$and": [{"role": "student"}, get_test_user_filter()]}
    """
    return {
        "username": {
            "$not": {"$regex": _TEST_USER_REGEX.pattern},
        }
    }
