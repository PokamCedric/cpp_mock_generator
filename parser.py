import yaml
from clang.cindex import Config, Index, CursorKind

# Replace '/usr/lib/llvm-13/lib' with the actual path where libclang-13.so is located
Config.set_library_path('/usr/lib/llvm-13/lib')

def parse_header(file_path, output_file):
    # Initialize the Clang index
    index = Index.create()

    # Parse the header file
    translation_unit = index.parse(file_path, args=['-x', 'c++', '-std=c++14'])

    output_data = []

    # Function to recursively visit nodes in the AST
    def visit_node(node, depth=0):
        node_data = {}
        if node.kind == CursorKind.FUNCTION_DECL:
            # Collect function details
            node_data = {
                'type': 'Function',
                'name': node.spelling,
                'return_type': node.result_type.spelling,
                'parameters': [
                    {'name': arg.spelling, 'type': arg.type.spelling}
                    for arg in node.get_arguments()
                ]
            }

        elif node.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
            # Collect class or struct details
            node_data = {
                'type': 'Class' if node.kind == CursorKind.CLASS_DECL else 'Struct',
                'name': node.spelling,
                'members_and_methods': []
            }
            # Visit children to find methods and members
            for child in node.get_children():
                if child.kind == CursorKind.CXX_METHOD:
                    node_data['members_and_methods'].append({
                        'type': 'Method',
                        'name': child.spelling,
                        'return_type': child.result_type.spelling,
                        'parameters': [
                            {'name': arg.spelling, 'type': arg.type.spelling}
                            for arg in child.get_arguments()
                        ]
                    })
                elif child.kind == CursorKind.FIELD_DECL:
                    node_data['members_and_methods'].append({
                        'type': 'Member',
                        'name': child.spelling,
                        'type': child.type.spelling
                    })

        if node_data:
            output_data.append(node_data)

        # Visit children
        for child in node.get_children():
            visit_node(child, depth + 1)

    # Start visiting nodes from the root of the AST
    visit_node(translation_unit.cursor)

    # Write the output data to a YAML file
    with open(output_file, 'w') as file:
        yaml.dump(output_data, file, sort_keys=False)

# Example usage
if __name__ == '__main__':
    header_file = 'test.h'  # Replace with the path to your header file
    output_yaml_file = 'output.yaml'  # Replace with the desired output file path
    parse_header(header_file, output_yaml_file)
