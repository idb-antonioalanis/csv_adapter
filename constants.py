# Reference separator that the files should have. It will be used to compare against.
REFERENCE_HEADER = [
    'mac',
    'dhcp60',
    'dhcp55',
    'hostname'
]

# The reference separator that the files should have. It will be used to compare against.
REFERENCE_SEPARATOR = ";"

# The separators to check for.
SEPARATORS = [",", ";", "\t", "|"]

# The directory where the input files are stored.
INPUT_FILES_DIRECTORY = "input_files"

# The directory where the valid and adapted files will be stored.
VALID_FILES_DIRECTORY = "valid_files"

# The directory where the invalid files will be stored.
INVALID_FILES_DIRECTORY = "invalid_files"
