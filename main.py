import os
import sys
import yaml
from cppparser import CppParser
from mock_generator import generate_mock_files  # Assurez-vous que cette importation est correcte

def save_to_yaml(data, output_file):
    """Save the parsed data to a YAML file."""
    with open(output_file, 'w') as file:
        yaml.dump(data, file, sort_keys=False)

def parse_and_save(file_path, output_directory):
    """Parse a single header file and save the result to a YAML file."""
    parser = CppParser()
    parsed_data = parser.parse_header([file_path])
    base_name = os.path.basename(file_path)
    output_file = os.path.join(output_directory, f"{os.path.splitext(base_name)[0]}_output.yaml")
    save_to_yaml(parsed_data, output_file)
    return output_file

def main(header_files, output_directory, parent_output_file):
    """Parse multiple header files and generate a parent YAML file that includes all individual outputs,
    then generate mock files based on the parent output YAML file."""
    all_data = []

    os.makedirs(output_directory, exist_ok=True)

    for header_file in header_files:
        output_file = parse_and_save(header_file, output_directory)
        all_data.append({
            'file': header_file,
            'output_file': output_file,
        })

    # Save the combined data to the parent output YAML file
    save_to_yaml(all_data, parent_output_file)

    # Generate mock files from the parent output YAML file
    generate_mock_files(parent_output_file, output_directory)

if __name__ == '__main__':
    # Get the header files from command line arguments
    header_files = sys.argv[1:]

    if not header_files:
        print("Please provide at least one header file to parse.")
        sys.exit(1)

    output_directory = 'outputs'  # Directory to save individual output files and mocks
    parent_output_file = os.path.join(output_directory, 'parent_output.yaml')  # File to save the combined output data

    main(header_files, output_directory, parent_output_file)
