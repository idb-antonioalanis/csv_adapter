import os
import glob
import shutil

import pandas as pd

from constants import (
    REFERENCE_HEADER,
    REFERENCE_SEPARATOR,
    SEPARATORS,
    INPUT_FILES_DIRECTORY,
    VALID_FILES_DIRECTORY,
    INVALID_FILES_DIRECTORY
)

from utils import find_best_match


class Adapter:
    """
        Adapter class for the batch processor.

        This will adapt every input file to the format expected by the batch processor.

        If the file is impossible to adapt, it will be copied to an invalid files directory. Otherwise, it will be adapted and copied to a valid files directory.

        Attributes:
            _file_names (list): The list of file names to adapt.
            _paths (list): The list of paths to the files to adapt.
    """

    def __init__(self):
        self._start_time = pd.Timestamp.now()

        self._file_names = [
            os.path.basename(path)
            for path in glob.glob(
                os.path.join(INPUT_FILES_DIRECTORY, "*.csv")
            )
        ]
        self._paths = [
            os.path.join(
                INPUT_FILES_DIRECTORY,
                file_name
            )
            for file_name in self._file_names
        ]

    def _detect_separator(self, path, rows_to_check=3):
        """
            Detects the separator used in a CSV file.

            It will read the first `self.ROWS_TO_CHECK` rows of the file and count the occurrences of each separator in the rows. The separator with the highest count will be returned.

            Args:
                path (str): The path to the file to detect the separator.
                rows_to_check (int): The number of rows to check for the separator. Defaults to 3.

            Returns:
                str: The detected separator.
        """
        separators_counter = {}

        with open(path, 'r') as file:
            for _ in range(rows_to_check):
                line = file.readline()

                if not line:
                    break

                for separator in SEPARATORS:
                    if separator in line:
                        separators_counter.setdefault(separator, 0)
                        separators_counter[separator] += 1

        return max(separators_counter, key=separators_counter.get)

    def _map_fields(self, header_fields):
        """
            Maps the fields in the header to the reference header.

            Duplicated fields will be mapped to the same reference field and fields with no match will be mapped to None.

            For example, if the header is ['ID', 'MAC', 'Hostname', 'ID', '??'] and the reference header is ['id', 'mac', 'dhcp60', 'hostname', 'dhcp55'], the function will return {'ID': ['id', 'id'], 'MAC': ['mac'], 'Hostname': ['hostname'], '??': [None]}.

            Args:
                fields (list): The fields in the header.

            Returns:
                dict: A dictionary where the keys are the fields in the header and the values are the best matches in the reference header.
        """
        header_mapped_fields = {}

        for field in header_fields:
            header_mapped_fields.setdefault(field, [])
            best_match = find_best_match(field, REFERENCE_HEADER)
            header_mapped_fields[field].append(best_match)

        return header_mapped_fields

    def _is_valid_header(self, header_mapped_fields):
        """
            Checks if the header is valid.

            The header is considered valid if there are no duplicated fields and if the reference header is a own subset of it.

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
            set(REFERENCE_HEADER) -
            set(flattened_header_mapped_fields_values)
        )

        if not duplicated_fields and not missing_fields:
            return True

        duplicated_fields and print(f"Error. {duplicated_fields} duplicated.")
        missing_fields and print(f"Error. {missing_fields} missing.")

        return False

    def _format(self, df, header_mapped_fields):
        """
            Formats the DataFrame by renaming the columns, dropping the columns with no match and rearranging the columns according to the reference header.

            Args:
                df (pd.DataFrame): The DataFrame to adapt.
                header_mapped_fields (dict): A dictionary where the keys are the fields in the header and the values are the best matches in the reference header.
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

        if df.columns.tolist() != REFERENCE_HEADER:
            df = df[REFERENCE_HEADER]
            print("Columns rearranged.")

        print("File formatted.")

        return df

    def _build(self, df, separator, file_name):
        """
            Builds the adapted CSV file with the reference separator.

            Args:
                df (pd.DataFrame): The DataFrame to build the CSV file from.
                separator (str): The separator to use in the CSV file.
                file_name (str): The name of the file to build.
        """
        if not os.path.exists(VALID_FILES_DIRECTORY):
            os.makedirs(VALID_FILES_DIRECTORY)

        df.to_csv(
            os.path.join(VALID_FILES_DIRECTORY, file_name),
            sep=REFERENCE_SEPARATOR,
            index=False
        )

        if separator != REFERENCE_SEPARATOR:
            print(
                f"Separator '{separator}' changed to '{
                    REFERENCE_SEPARATOR}'."
            )

        print(f"File built in '{VALID_FILES_DIRECTORY}/'.")

    def _copy(self, file_name):
        """
            Copies a file that were impossible to adapt to an invalid files directory.

            Args:
                file_name (str): The name of the file that was impossible to adapt.
        """
        if not os.path.exists(INVALID_FILES_DIRECTORY):
            os.makedirs(INVALID_FILES_DIRECTORY)

        shutil.copy(
            os.path.join(INPUT_FILES_DIRECTORY, file_name),
            os.path.join(INVALID_FILES_DIRECTORY, file_name)
        )

        print(f"File copied to '{INVALID_FILES_DIRECTORY}/'.")

    def _proccess(self):
        """
            All the processing steps for the adapter, returning the list of adapted or already valid files.

            Returns:
                list: The list of adapted or already valid files.
        """
        valid_files = []

        for file_name, path in zip(self._file_names, self._paths):
            separator = self._detect_separator(path)
            df = pd.read_csv(path, sep=separator)

            print(f"\nFile '{file_name}'.")

            header = df.columns.tolist()

            if header == REFERENCE_HEADER and separator == REFERENCE_SEPARATOR:
                print("The file already has the correct format.")
                self._build(df, separator, file_name)
                valid_files.append(file_name)
                continue

            header_mapped_fields = self._map_fields(header)

            if not self._is_valid_header(header_mapped_fields):
                print("Invalid file.")
                self._copy(file_name)
                print("This file will be skipped.")
                continue

            df = self._format(df, header_mapped_fields)
            self._build(df, separator, file_name)

            valid_files.append(file_name)

        return valid_files

    def adapt(self):
        """
            Runs the adapter. Returns the list of adapted or already valid files.

            Returns:
                list: The list of adapted or already valid files.
        """
        valid_files = self._proccess()

        print(
            f"\n{self.__class__.__name__} tasks completed. Execution time - {pd.Timestamp.now() - self._start_time}.", end="\n\n"
        )

        return valid_files
