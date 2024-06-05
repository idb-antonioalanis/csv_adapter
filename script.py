import os

import difflib
import re

import pandas as pd


# Reference header to compare against.
REFERENCE_HEADER = [
    'mac',
    'dhcp60',
    'dhcp55',
    'hostname'
]

# Reference separator.
REFERENCE_SEPARATOR = ';'

# Name of the CSV file.
FILE_NAME = "correct.csv"

# Path to the CSV file.
FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "test_files",
    FILE_NAME
)

# Output path for the adapted CSV file.
OUTPUT_FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "output_files",
    FILE_NAME
)

# List of possible separators.
SEPARATORS = [',', ';', '\t', '|']

# Number of rows to check for detecting the separator.
ROWS_TO_CHECK = 3


def detect_separator(path, rows_to_check=ROWS_TO_CHECK, separators=SEPARATORS):
    """
        Detects the separator used in a CSV file.

        It will read the first `rows_to_check` rows of the file and count the occurrences of each separator in the rows. The separator with the highest count will be returned.

        Args:
            path (str): The path to the CSV file.
            rows_to_check (int): The number of rows to check for the separator.

        Returns:
            str: The detected separator.
    """
    separators_counter = {}

    with open(path, 'r') as file:
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


def find_best_match(string, choices):
    """
        Finds the best match for a string in a list of choices.

        It will use `difflib` to find the best match for the string in the list of choices.

        If the best match has a similarity score greater than or equal indicated by the `cutoff` parameter, it will return the choice.

        Args:
            name (str): The string to find the best match for.
            choices (list): The list of choices to search for a match.

        Returns:
            str: The best match for the string in the list of choices or the string itself if no match is found.
            None: If no match is found and no string is returned.
    """
    normalized_name = normalize(string)

    best_match = difflib.get_close_matches(
        normalized_name,
        choices,
        n=1,
        cutoff=0.6
    )

    if not best_match:
        return None

    return best_match[0]


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


def is_valid_header(header_mapped_fields, file_name=FILE_NAME, reference_header=REFERENCE_HEADER):
    """
        Checks if the header is valid and returns a feedback message.

        The header is considered valid if there are no duplicated fields and if it is a subset of the reference header.

        Args:
            header_mapped_fields (dict): A dictionary where the keys are the fields in the header and the values are the best matches in the reference header.

        Returns:
            bool: True if the header is valid, False otherwise.
    """
    flattened_header_mapped_fields_values = []

    duplicated_fields = []
    missing_fields = []

    for field, matches in header_mapped_fields.items():
        flattened_header_mapped_fields_values.extend(matches)

        if len(matches) > 1:
            duplicated_fields.append(field)

    missing_fields = list(
        set(reference_header) - set(flattened_header_mapped_fields_values)
    )

    if not duplicated_fields and not missing_fields:
        return True

    print(f"Error in file '{file_name}'.")
    duplicated_fields and print(f"{duplicated_fields} duplicated.")
    missing_fields and print(f"{missing_fields} missing.")

    return False


def adapt_df(df, header_mapped_fields, reference_header=REFERENCE_HEADER):
    """
        Adapts the DataFrame by renaming the columns, dropping the columns with no match and rearranging the columns according to the reference header.

        Args:
            df (pd.DataFrame): The DataFrame to adapt.
            header_mapped_fields (dict): A dictionary where the keys are the fields in the header and the values are the best matches in the reference header.
            reference_header (list): The reference header to order the columns.
    """
    for field, matches in header_mapped_fields.items():
        match_ = matches[0]

        if match_ is None:
            df.drop(columns=field, inplace=True)

            print(f"Column '{field}' dropped.")

            continue

        if field != match_:
            df.rename(columns={field: match_}, inplace=True)

            print(f"Column '{field}' renamed to '{match_}'.")

    if df.columns.tolist() != reference_header:
        df = df[reference_header]

        print("Columns rearranged.")

    return df


def build(df, separator, reference_separator=REFERENCE_SEPARATOR):
    """
        Builds the adapted CSV file.

        Args:
            df (pd.DataFrame): The DataFrame to build the CSV file from.
            separator (str): The separator to use in the CSV file.
            reference_separator (str): The reference separator to compare against.
    """
    if not os.path.exists(os.path.dirname(OUTPUT_FILE_PATH)):
        os.makedirs(os.path.dirname(OUTPUT_FILE_PATH))

    df.to_csv(OUTPUT_FILE_PATH, sep=reference_separator, index=False)

    if separator != reference_separator:
        print(f"Separator '{separator}' changed to '{reference_separator}'.")


def run():
    """
        Runs the script.
    """
    separator = detect_separator(FILE_PATH)

    df = pd.read_csv(FILE_PATH, sep=separator)

    print(f"File '{FILE_NAME}'.")

    header = df.columns.tolist()

    if header == REFERENCE_HEADER and separator == REFERENCE_SEPARATOR:
        print("The file already has the correct format.")

        return

    if header != REFERENCE_HEADER:
        header_mapped_fields = map_fields(header)

        if not is_valid_header(header_mapped_fields):
            print("Invalid file. Skipped.")

            return

        adapt_df(df, header_mapped_fields)

    build(df, separator)

    print("File adapted.")


if __name__ == "__main__":
    start_time = pd.Timestamp.now()
    run()
    print(f"Execution time - {pd.Timestamp.now() - start_time}")
