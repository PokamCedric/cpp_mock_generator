import os
import yaml

def generate_mock_files_from_yaml(yaml_file, output_directory):
    """Generate mock header files from YAML data."""
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    mock_files = []
    for entry in data:
        file_name = os.path.basename(entry['file'])
        class_name = os.path.splitext(file_name)[0]

        # Generate mock header content
        mock_content = generate_mock_header(entry)
        mock_file_path = os.path.join(output_directory, f"{class_name}_mock.hpp")

        # Write mock header to file
        with open(mock_file_path, 'w') as mock_file:
            mock_file.write(mock_content)

        mock_files.append(mock_file_path)

    return mock_files

def generate_mock_header(entry):
    """Generate mock header content for a class."""
    class_name = os.path.splitext(os.path.basename(entry['file']))[0]

    mock_header = f"""
    // {class_name}_mock.hpp
    #ifndef {class_name.upper()}_MOCK_HPP
    #define {class_name.upper()}_MOCK_HPP

    #include "{class_name}.h"
    #include <gmock/gmock.h>

    class Mock{class_name} : public {class_name} {{
    public:"""

    for method in entry['methods']:
        mock_header += f"""
        MOCK_METHOD({method['return_type']}, {method['name']}, ({", ".join([arg['type'] + ' ' + arg['name'] for arg in method['parameters']])}), (override));"""

    mock_header += f"""
    }};

    #endif // {class_name.upper()}_MOCK_HPP
    """

    return mock_header
