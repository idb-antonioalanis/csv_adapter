import os

import difflib
import re

import pandas as pd


# Reference header to compare against.
REFERENCE_HEADER = ['id', 'mac', 'dhcp60',
                    'hostname', 'dhcp55']

# Path to the CSV file.
FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "test_files",
    "Datos PRO BR - 1 abril copy extra field.csv"
)

# List of possible separators.
SEPARATORS = [',', ';', '\t']

# Number of rows to check for the separator.
ROWS_TO_CHECK = 3


def detect_separator(filename, rows_to_check=ROWS_TO_CHECK, separators=SEPARATORS):
    """
        Detects the separator used in a CSV file.

        It will read the first `rows_to_check` rows of the file and count the occurrences of each separator in the rows. The separator with the highest count will be returned.

        Args:
            filename (str): The path to the CSV file.
            rows_to_check (int): The number of rows to check for the separator.

        Returns:
            str: The detected separator.
    """
    separators_counter = {}

    with open(filename, 'r') as file:
        for _ in range(rows_to_check):
            line = file.readline()

            if not line:
                break

            for separator in separators:
                if separator in line:
                    separators_counter.setdefault(separator, 0)

                    separators_counter[separator] += 1

    return max(separators_counter, key=separators_counter.get)


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
            None: If no match is found and no string is returned.
    """
    normalized_name = normalize(name)

    best_match = difflib.get_close_matches(
        normalized_name,
        choices,
        n=1,
        cutoff=0.6
    )

    if not best_match:
        return None

    index = choices.index(best_match[0])
    best_match = choices[index]

    return best_match


def map_fields(fields, reference_header=REFERENCE_HEADER):
    """
        Maps the fields in the header to the reference header.

        Duplicated fields will be mapped to the same reference field and fields with no match will be mapped to None.

        For example, if the header is ['ID', 'MAC', 'Hostname', 'ID', '??'] and the reference header is ['id', 'mac', 'dhcp60', 'hostname', 'dhcp55'], the function will return {'ID': ['id', 'id'], 'MAC': ['mac'], 'Hostname': ['hostname'], '??': [None]}.

        Args:
            fields (list): The fields in the header.
            reference_header (list): The reference header to compare against.

        Returns:
            dict: A dictionary where the keys are the fields in the header and the values are the best matches in the reference header.
    """
    mapped_fields = {}

    for field in fields:
        mapped_fields.setdefault(field, [])

        best_match = find_best_match(field, reference_header)

        mapped_fields[field].append(best_match)

    return mapped_fields


def get_mapped_fields_list(mapped_fields):
    """
        Returns the list of mapped fields. 

        If a field was duplicated, it will only return the first match. If a field had no match, it will not be included in the list.

        For example, if the mapped fields are {'ID': ['id', 'id'], 'MAC': ['mac'], 'Hostname': ['hostname'], '??': [None]}, the function will return ['id', 'mac', 'hostname'].

        Args:
            mapped_fields (dict): The mapped fields.

        Returns:
            list: The list of mapped fields. 
    """
    mapped_fields_list = []

    for _, matches in mapped_fields.items():
        if len(matches) >= 1:
            match_ = matches[0]

            if match_ is not None:
                mapped_fields_list.append(match_)

    return mapped_fields_list


def is_valid_header(header, reference_header=REFERENCE_HEADER):
    """
        Checks if the header is valid and returns a feedback message.

        Args:
            header (list): The header to validate.
            reference_header (list): The reference header to compare against.

        Returns:
            bool: True if the header is valid, False otherwise.
    """
    def get_mapped_fields_list(mapped_fields):
        """
            Returns the list of mapped fields. 

            If a field was duplicated, it will only return the first match. If a field had no match, it will not be included in the list.

            For example, if the mapped fields are {'ID': ['id', 'id'], 'MAC': ['mac'], 'Hostname': ['hostname'], '??': [None]}, the function will return ['id', 'mac', 'hostname'].

            Args:
                mapped_fields (dict): The mapped fields.

            Returns:
                list: The list of mapped fields. 
        """
        mapped_fields_list = []

        for _, matches in mapped_fields.items():
            if len(matches) >= 1:
                match_ = matches[0]

                if match_ is not None:
                    mapped_fields_list.append(match_)

        return mapped_fields_list

    header_mapped_fields_list = get_mapped_fields_list(header)

    differences = set(header_mapped_fields_list) ^ set(reference_header)

    if differences:
        print(f"Invalid header. {differences} not in {reference_header}.")

        return False

    print("Valid header.")

    return True


if __name__ == "__main__":
    separator = detect_separator(FILE_PATH)

    df = pd.read_csv(FILE_PATH)

    header = df.columns.tolist()[0].split(separator)

    header_mapped_fields = map_fields(header)

    is_valid_header(header_mapped_fields)
