import os

import difflib
import re

import pandas as pd

REFERENCE_HEADER = [
    'id', 'mac', 'dhcp60', 'hostname', 'dhcp55', 'device_category',
    'device_type', 'device_name', 'device_os', 'device_manufacturer',
    'device_additional_info', 'inference_key', 'random_mac', 'candidates_categories'
]

FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "test_files",
    "rules-categorizations_20240401000005_7d0233eb-679f-4d86-8c67-9abe89c3f557.csv"
)


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
        if field not in REFERENCE_HEADER:
            mapped_fields.remove(field)

    mapped_fields = list(set(mapped_fields))

    return mapped_fields


def map_fields(fields, reference_header=REFERENCE_HEADER):
    """
        Maps a list of input fields to the closest matching fields in the list of known fields.
    """
    mapped_fields = [
        find_best_match(field, reference_header) for field in fields
    ]
    mapped_fields = delete_unnecessary_mapped_fields(mapped_fields)

    return mapped_fields


def is_valid_header(header, reference_header=REFERENCE_HEADER):
    """
        Checks if the header is valid returning a feedback message.

        Args:
            header (list): The header to validate.
            reference_header (list): The reference header to compare against.

        Returns:
            bool: True if the header is valid, False otherwise.
    """
    differences = set(header) ^ set(reference_header)

    if differences:
        return print(f"Invalid header. {differences} not in {reference_header}.") and False

    return print("Valid header.") and True


if __name__ == "__main__":
    df = pd.read_csv(FILE_PATH)

    header = df.columns.tolist()

    header_mapped_fields = map_fields(header)

    is_valid_header(header_mapped_fields)
