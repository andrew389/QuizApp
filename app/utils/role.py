from enum import Enum


class Role(Enum):
    """
    Enum representing various roles within the application.

    Attributes:
        UNEMPLOYED (int): Indicates a user without a specific role.
        OWNER (int): Indicates a user who owns a company or entity.
        ADMIN (int): Indicates a user with administrative privileges.
        MEMBER (int): Indicates a regular member of a company or entity.
    """

    UNEMPLOYED = 0
    OWNER = 1
    ADMIN = 2
    MEMBER = 3
