import difflib
import re

FIELDS = [
    'id', 'mac', 'dhcp60', 'hostname', 'dhcp55', 'device_category',
    'device_type', 'device_name', 'device_os', 'device_manufacturer',
    'device_additional_info', 'inference_key', 'random_mac', 'candidates_categories'
]


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


def find_best_match(name, choices):
    """
        Finds the best match for a string in a list of choices.

        It will use `difflib` to find the best match for the string in the list of choices. If the best match has a similarity score greater than or equal indicated by the `cutoff` parameter, it will return the choice. Otherwise, it will return the string itself.

        Args:
            name (str): The string to find the best match for.
            choices (list): The list of choices to search for a match.

        Returns:
            str: The best match for the string in the list of choices or the string itself if no match is found.
    """
    normalized_name = normalize(name)

    best_match = difflib.get_close_matches(
        normalized_name,
        choices,
        n=1,
        cutoff=0.6
    )

    if best_match:
        index = choices.index(best_match[0])
        best_match = choices[index]

        return best_match

    return name


def delete_unnecessary_mapped_fields(mapped_fields):
    """
        Deletes unnecessary mapped fields.

        If there is a mapped field that is not in the list of known fields or is a duplicate, it will be removed from the list of mapped fields.
    """
    for field in mapped_fields:
        if field not in FIELDS:
            mapped_fields.remove(field)

    mapped_fields = list(set(mapped_fields))

    return mapped_fields


def map_fields(fields):
    """
        Maps a list of input fields to the closest matching fields in the list of known fields.
    """
    mapped_fields = [find_best_match(field, FIELDS) for field in fields]
    mapped_fields = delete_unnecessary_mapped_fields(mapped_fields)

    return mapped_fields


if __name__ == "__main__":
    second_list = [
        'Categorization date', 'MAC', 'DHCP 60', 'DHCP 55', 'Host name',
        'Device category', 'Device type', 'Device name', 'Device OS',
        'Device manufacturer', 'Is it a random mac?', 'Inference key',
        'Device additional info', 'Rules file name', 'Candidates'
    ]

    print(f"First list: {FIELDS}", end="\n\n")

    print(f"Second list: {second_list}", end="\n\n")

    mapped_fields = map_fields(second_list)

    print(f"Mapped fields from Second list: {mapped_fields}", end="\n\n")

    print(f"Is the mapped fields list the same as the known fields list? {
        mapped_fields == FIELDS}")

    print(f"Their difference is: {set(mapped_fields) ^ set(FIELDS)}")
