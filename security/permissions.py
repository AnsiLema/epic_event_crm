def has_permission(payload: dict, allowed_role: list[str]) -> bool:
    """
    Check if the user has the required permission based on their role.

    This function verifies whether the user's role, as provided in the payload, is
    included within the allowed roles.

    :param payload: A dictionary containing user information, specifically the
        user's role.
    :param allowed_role: A list of roles that are permitted access.
    :return: A boolean value indicating if the user has the required permission.
    """
    if not isinstance(payload, dict):
        raise TypeError("Payload doit être un dictionnaire.")

    user_role = payload.get("role")
    if user_role is None:
        return False

    return user_role in allowed_role


def can_manage_collaborators(payload: dict) -> bool:
    """
    Determines whether a user has the permission to manage collaborators.

    The function checks if the given payload contains the necessary
    permissions to manage collaborators by using the `has_permission`
    utility.

    :param payload: The dictionary containing user permissions and
                    other related information.
    :type payload: dict
    :return: True if the user can manage collaborators, False otherwise.
    :rtype: bool
    """
    if not isinstance(payload, dict):
        raise TypeError("Payload doit être un dictionnaire.")

    role = payload.get("role")
    if role is None:
        return False

    return has_permission(payload, ["gestion"])


def can_manage_contracts(payload: dict) -> bool:
    """
    Determines if the user has the required permissions to manage contracts. This function
    checks the permissions included in the payload against the required permissions
    for contract management.

    :param payload: A dictionary containing user permission data.
    :type payload: dict
    :return: A boolean indicating whether the user has the required permissions.
    :rtype: bool
    """
    if not isinstance(payload, dict):
        raise TypeError("Payload doit être un dictionnaire.")

    role = payload.get("role")
    if role is None:
        return False

    return has_permission(payload, ["gestion", "commercial"])


def can_manage_events(payload: dict) -> bool:
    """
    Determines if the user has the permissions to manage events.

    This function evaluates whether the user, defined by the payload, has
    specific required permissions to manage events. The permissions checked
    are "gestion" and "support".

    :param payload: Dictionary containing user information, typically including
        roles and permissions.
    :type payload: dict
    :return: True if the user possesses the required permissions, False otherwise.
    :rtype: bool
    """
    if not isinstance(payload, dict):
        raise TypeError("Payload doit être un dictionnaire.")

    role = payload.get("role")
    if role is None:
        return False

    return has_permission(payload, ["gestion", "support"])


def can_manage_own_clients(payload: dict) -> bool:
    """
    Determines if the user has permission to manage their own clients.

    This function checks whether the provided payload includes the required
    permissions to allow a user to manage their own commercial clients. The check
    is specifically looking for the presence of the "commercial" permission in
    the provided payload.

    :param payload: The dictionary containing user permissions and other
        authorization details.
    :type payload: dict
    :return: True if the user has "commercial" permissions; otherwise, False.
    :rtype: bool
    """
    if not isinstance(payload, dict):
        raise TypeError("Payload doit être un dictionnaire.")

    role = payload.get("role")
    if role is None:
        return False

    return has_permission(payload, ["commercial"])


def is_commercial(payload: dict) -> bool:
    """
    Determines whether the provided payload indicates a commercial role.

    This function evaluates the `role` field within the given `payload` to
    check if it is marked as "commercial". If the `role` key does not
    exist, the function will return False.

    :param payload: Dictionary containing the data to be evaluated. The key
        `role` is expected to exist within the dictionary to determine
        if the role is "commercial".
    :return: Boolean value indicating whether the role in the payload is
        "commercial".
    """
    if not isinstance(payload, dict):
        raise TypeError("Le payload doit être un dictionnaire.")
    return payload.get("role") == "commercial"


def is_support(payload: dict) -> bool:
    """
    Checks if the given payload signifies a support role.

    This function evaluates the provided payload dictionary and
    determines if the 'role' key within the dictionary is set
    to 'support'. It is designed to work with structured data
    where roles are specified as part of the payload.

    :param payload: A dictionary containing a 'role' key which
        specifies the type of role.
    :type payload: dict
    :return: Returns True if the 'role' in payload is 'support',
        otherwise False.
    :rtype: bool
    """
    if not isinstance(payload, dict):
        raise TypeError("Le payload doit être un dictionnaire.")
    return payload.get("role") == "support"
