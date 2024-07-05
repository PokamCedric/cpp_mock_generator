from parser import parse_header, save_to_yaml

# Example usage
if __name__ == '__main__':
    header_files = ['test/base.h', 'test/derived.h', 'test/features.h']  # Replace with the paths to your header files
    output_yaml_file = 'test/output.yaml'  # Replace with the desired output file path

    # Parse the header files
    parsed_data = parse_header(header_files)

    # Save the parsed data to a YAML file
    save_to_yaml(parsed_data, output_yaml_file)
