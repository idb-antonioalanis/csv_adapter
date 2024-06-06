import re
import difflib


def normalize(name):
    """
        Normalizes a string by converting it to lowercase, removing leading and trailing whitespaces, and replacing spaces with underscores.

        For example, '  Device Name ' becomes 'device_name'.

        Args:
            name (str): The string to normalize.

        Returns:
            str: The normalized string.
    """
    return re.sub(r'\s+', '_', name.strip().lower())


def find_best_match(string, choices, cutoff=0.6):
    """
        Finds the best match for a string in a list of choices.

        It will use `difflib` to find the best match for the string in the list of choices. 

        If the best match has a similarity score greater than or equal indicated by the `cutoff` parameter, it will return the choice.

        Args:
            name (str): The string to find the best match for.
            choices (list): The list of choices to search for a match.
            cutoff (float): The similarity score cutoff to consider a match. Defaults to 0.6.

        Returns:
            str: The best match for the string in the list of choices or the string itself if no match is found.
            None: If no match is found and no string is returned.
    """
    normalized_string = normalize(string)

    best_match = difflib.get_close_matches(
        normalized_string,
        choices,
        n=1,
        cutoff=cutoff
    )

    if not best_match:
        return None

    return best_match[0]
