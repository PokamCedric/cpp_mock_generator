import os
from parser import main


if __name__ == '__main__':
    import sys

    # Get the header files from command line arguments
    header_files = sys.argv[1:]

    if not header_files:
        print("Please provide at least one header file to parse.")
        sys.exit(1)

    output_directory = 'outputs'  # Directory to save individual output files
    parent_output_file = 'parent_output.yaml'  # File to save the combined output data

    main(header_files, output_directory, parent_output_file)
