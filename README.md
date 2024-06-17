# csv_adapter

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Example](#example)

## Overview

This script provides an adapter that standardizes CSV files to a specific format expected.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/idb-antonioalanis/csv_adapter
    cd csv_adapter
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Set the `REFERENCE_HEADER` constant with the desired header format in the `constants.py` file.

2. Place the CSV files to be adapted in the `input_files` directory.

3. Run the adapter with the following command:
    ```bash
    python script.py
    ```

### Example

    $ python script.py               

    File 'correct.csv'.
    The file already has the correct format.
    File built in 'valid_files/'.

    File 'extrafield-rename.csv'.
    Column 'ID' dropped.
    Column 'extrafield' dropped.
    Columns rearranged.
    File formatted.
    Separator ',' changed to ';'.
    File built in 'valid_files/'.

    File 'order-extrafield-rename.csv'.
    Column 'ID' dropped.
    Column 'extrafield' dropped.
    Columns rearranged.
    File formatted.
    Separator ',' changed to ';'.
    File built in 'valid_files/'.

    File 'rules-categorizations_20240601190004_78df76c2-e923-4b09-9b35-d985047b82ef.csv'.
    Column 'Categorization date' dropped.
    Column 'MAC' renamed to 'mac'.
    Column 'DHCP 60' renamed to 'dhcp60'.
    Column 'DHCP 55' renamed to 'dhcp55'.
    Column 'Host name' renamed to 'hostname'.
    Column 'Device category' dropped.
    Column 'Device type' dropped.
    Column 'Device name' dropped.
    Column 'Device OS' dropped.
    Column 'Device manufacturer' dropped.
    Column 'Is it a random mac?' dropped.
    Column 'Inference key' dropped.
    Column 'Device additional info' dropped.
    Column 'Rules file name' dropped.
    Column 'Candidates' dropped.
    File formatted.
    Separator ',' changed to ';'.
    File built in 'valid_files/'.

    File 'separator-extrafield-rename.csv'.
    Column 'ID' dropped.
    Column 'extrafield' dropped.
    Columns rearranged.
    File formatted.
    File built in 'valid_files/'.

    File 'separator-misleading_field-extrafield-rename.csv'.
    Column 'ID' dropped.
    Column 'extrafield' dropped.
    Columns rearranged.
    File formatted.
    File built in 'valid_files/'.

    Adapter tasks completed. Execution time - 0 days 00:00:00.539540.

    Valid files - [
        'extrafield-rename.csv', 
        'order-extrafield-rename.csv', 
        'rules-categorizations_20240601190004_78df76c2-e923-4b09-9b35-d985047b82ef.csv', 
        'separator-extrafield-rename.csv', 
        'separator-misleading_field-extrafield-rename.csv'
    ].
