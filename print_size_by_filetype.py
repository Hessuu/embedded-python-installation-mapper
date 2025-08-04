def print_dicts_side_by_side(dict_list, header_prefix="Directory"):
    """
    Prints a list of dictionaries in a side-by-side columnar format.

    Args:
        dict_list (list): A list of dictionaries to print.
        header_prefix (str): The prefix for column headers.
    """
    if not dict_list:
        print("The list of dictionaries is empty.")
        return

    # Step 1: Prepare the data for each column
    headers = [f"{header_prefix} {i+1}" for i in range(len(dict_list))]
    
    # Convert each dictionary's items into a list of "key: value" strings
    cols_as_strings = [
        [f"{key}: {value}" for key, value in d.items()]
        for d in dict_list
    ]

    # Step 2: Calculate the layout
    # Find the width for each column based on the longest item or header
    col_widths = [
        max(len(header), max((len(s) for s in col), default=0))
        for header, col in zip(headers, cols_as_strings)
    ]
    
    # Find the maximum number of rows needed
    num_rows = max(len(col) for col in cols_as_strings) if cols_as_strings else 0

    # Step 3: Print the formatted output
    # Print headers
    header_line = " | ".join(header.ljust(width) for header, width in zip(headers, col_widths))
    print(header_line)

    # Print separator
    separator_line = "-+-".join("-" * width for width in col_widths)
    print(separator_line)
    
    # Print data rows
    for i in range(num_rows):
        row_items = []
        for j, col in enumerate(cols_as_strings):
            try:
                # Get the i-th item from the j-th column
                item = col[i]
            except IndexError:
                # If a column has no more items, use an empty string
                item = ""
            row_items.append(item.ljust(col_widths[j]))
        print(" | ".join(row_items))
