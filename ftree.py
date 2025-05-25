import os
import argparse
import csv


def setup_parse_and_validate_args():
    """
    Method to set up and parse command line arguments
    :return: tuple containing the CSV file name and hierarchy columns
    :raises: RuntimeError if 'nodes' is used as a hierarchy column or if the CSV file does not exist
    """
    parser = argparse.ArgumentParser(
        description="Render a tree-structured CSV file to ASCII table with node counts"
    )

    parser.add_argument("csv_file", type=str, help="Path to the CSV file containing the tree structure")
    parser.add_argument("-d", required=True,
                        help="Comma separated list of columns forming the tree hierarchy (top to bottom)")

    args = parser.parse_args()

    # validate for nodes in args.d
    if 'nodes' in args.d:
        raise RuntimeError("Nodes column is reserved and cannot be used in the hierarchy definition")

    # validate CSV file existence
    if not os.path.isfile(args.csv_file):
        raise RuntimeError(f"CSV file '{args.csv_file}' does not exist")

    # parse hierarchy columns to a list
    columns = args.d.split(",")

    return args.csv_file, columns


def read_csv_file(file_name: str) -> tuple[list, list[str]]:
    """
    Method to read a CSV file and return its content as a list of dictionaries

    :param file_name: Path to the CSV file
    :return: return list of dictionaries representing the rows in the CSV file
    """
    with open(file_name, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames)


def calculate_tree_nodes(tree_rows: list, seniority_columns: list[str]):
    """
    Method to calculate the number of nodes in a tree structure based on seniority columns

    Strategy:
        1. Calculate the seniority level based on first non-empty column in each row
        2. Loop through the rows and calculate the number of children for each node
        3. Assign the number of children to each row

    :param tree_rows: List of dictionaries representing the rows in the tree structure
    :param seniority_columns: List of columns that define the hierarchy (from top to bottom)
    :return: list of dictionaries with the original row data and the calculated 'nodes' count
    """

    # 1. calculate seniority level for each row
    rows_with_seniority = []

    # loop through each row and find the first column that has a value
    for row_idx, tree_row in enumerate(tree_rows):

        row_seniority = None

        # loop through seniority columns to find the first non-empty value
        # the lower the seniority column index, the higher the seniority level (0 is the highest)
        for seniority_column_index, seniority_column in enumerate(seniority_columns):

            # check if the column exists in the row
            if seniority_column not in tree_row:
                raise ValueError(f"Column '{seniority_column}' not found in row {tree_row}")

            # skip empty strings - meaning we are not interested in unfilled column values
            if tree_row[seniority_column] == "":
                continue

            # if that column exists, and it's not empty, we found the seniority level
            row_seniority = seniority_column_index
            break

        # if failed to find a value in seniority columns, raise an error
        if row_seniority is None:
            raise ValueError(f"Row {row_idx} has no value in tree columns")

        rows_with_seniority.append({
            "row": tree_row,
            "level": row_seniority,
            "children": 0,  # initialize children count
        })

    # 2. calculate children count based on seniority
    parent_stack = []  # keep track of latest parent at each level

    # loop through rows with seniority
    for row in rows_with_seniority:
        level = row["level"]

        # validate possible level jumps
        if level > len(parent_stack):
            raise ValueError(
                f"Invalid tree structure at row {row['row']} - "
                f"level jumps from {len(parent_stack) - 1} to {level}"
            )

        # if we are at the same level as the last parent, we can just append
        if level == len(parent_stack):
            parent_stack.append(row)

        # if different level, we need to adjust the stack
        else:
            parent_stack = parent_stack[:level + 1]
            parent_stack[level] = row

        # if level is not base level - add child count to the parent
        if level > 0:
            parent = parent_stack[level - 1]
            parent["children"] = parent.get("children", 0) + 1

    # 3. assign node values and change 0s to empty strings if needed
    for row_with_seniority in rows_with_seniority:
        nodes = row_with_seniority["children"]
        row_with_seniority["row"]["nodes"] = str(nodes) if nodes else ""

    # 4. return list of rows with nodes
    return [item["row"] for item in rows_with_seniority]


def create_table(tree_rows, columns) -> str:
    """
    Method that creates a string element for table representation of the tree structure
        (also adds padding to the cells based on the longest value in the rows)

    :param tree_rows: Rows of the table
    :param columns: Columns of the table
    :return: str representation of the table with padded cells
    """
    # add header to the table rows
    created_table_rows = [columns]

    # from list of dicts convert to lists with values based on columns
    for row in tree_rows:
        row_values = [str(row.get(col, "") or "") for col in columns]
        created_table_rows.append(row_values)

    # calculate column WIDTHS for nice spacing for the table
    col_widths = []

    # loop through each column index
    for i in range(len(columns)):
        # go through every row and find the longest value in that column
        max_length = max(len(str(row[i])) for row in created_table_rows)
        col_widths.append(max_length)

    # create a method that formats (adds padding) each row based on the column widths that we just generated
    def add_padding_to_row(raw_row):
        padded_cells = []
        for row_idx in range(len(columns)):
            cell = raw_row[row_idx].ljust(col_widths[row_idx])  # pad each cell to the column width (calculated before)
            padded_cells.append(cell)
        return " | ".join(padded_cells)

    # pad rows, join them and add \n at the end of each row
    return "\n".join(add_padding_to_row(row) for row in created_table_rows)


if __name__ == "__main__":
    # read command line args
    csv_file_name, passed_columns = setup_parse_and_validate_args()

    # read CSV file
    tree_data_rows, tree_data_columns = read_csv_file(csv_file_name)

    # calculate nodes
    tree_data_rows = calculate_tree_nodes(tree_data_rows, passed_columns)
    tree_data_rows = calculate_tree_nodes(tree_data_rows, passed_columns)
    tree_data_columns += ["nodes"]  # add 'nodes' column to the columns list

    # create table from the rows and columns
    table = create_table(tree_data_rows, tree_data_columns)
    print(table)
