import yaml
import os

def generate_mock_class(data):
    """Generate mock class based on the parsed class data."""
    class_name = data['name']
    mock_class_name = f'Mock{class_name}'
    mock_methods = []

    for method in data['methods']:
        if method['access'] == 'public':
            method_signature = generate_mock_method_signature(method)
            mock_methods.append(method_signature)

    friend_declaration = ''
    if 'friend_classes' in data:
        friend_declaration = '\n'.join([f'friend class {friend};' for friend in data['friend_classes']])

    mock_class = f"""
#ifndef {mock_class_name.upper()}_HPP
#define {mock_class_name.upper()}_HPP

#include "{class_name.lower()}.h"
#include <gmock/gmock.h>

class {mock_class_name} : public {class_name} {{
public:
    {friend_declaration}
    {''.join(mock_methods)}
}};

#endif // {mock_class_name.upper()}_HPP
"""
    return mock_class

def generate_mock_method_signature(method):
    """Generate mock method signature."""
    return_type = method['return_type']
    method_name = method['name']
    parameters = ', '.join([f'{param["type"]} {param["name"]}' for param in method['parameters']])
    const_qualifier = 'const' if method['is_const'] else ''
    method_signature = f'MOCK_METHOD({return_type}, {method_name}, ({parameters}), ({const_qualifier}, override));\n'
    return method_signature

def generate_mock_files(parent_output, output_directory):
    """Generate mock files based on the parent output YAML file."""
    with open(parent_output, 'r') as file:
        data = yaml.safe_load(file)

    for entry in data:
        file = entry['file']
        output_file = entry['output_file']

        with open(output_file, 'r') as f:
            parsed_data = yaml.safe_load(f)

        for item in parsed_data:
            if item['type'] == 'Class':
                mock_content = generate_mock_class(item)
                class_name = item['name']
                mock_file_path = os.path.join(output_directory, f'Mock{class_name}.hpp')

                with open(mock_file_path, 'w') as mock_file:
                    mock_file.write(mock_content)

                print(f'Mock file generated: {mock_file_path}')
