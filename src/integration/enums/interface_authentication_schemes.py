from integration.enums.custom_enum import CustomEnum


class InterfaceAuthenticationScheme(CustomEnum):
    """Represents the type of Authentication used on Device Interface"""

    basic = "basic"
    """Basic Authentication, featuring username and password"""
