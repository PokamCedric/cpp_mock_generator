import yaml
from clang.cindex import Config, Index, CursorKind, TokenKind

# Replace '/usr/lib/llvm-13/lib' with the actual path where libclang-13.so is located
Config.set_library_path('/usr/lib/llvm-13/lib')

def parse_header(file_paths):
    # Initialize the Clang index
    index = Index.create()

    output_data = []
    processed_classes = {}  # Dictionary to store processed classes by name

    def process_translation_unit(tu):
        # Function to recursively visit nodes in the AST
        def visit_node(node, depth=0):
            node_data = {}
            if node.kind == CursorKind.FUNCTION_DECL and not node.semantic_parent.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
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

            elif node.kind == CursorKind.CLASS_DECL:
                # Collect class details
                node_data = {
                    'type': 'Class',
                    'name': node.spelling,
                    'base_classes': [],
                    'members': [],
                    'methods': [],
                    'static_members': []
                }

                # Check for base classes (inheritance)
                for base in node.get_children():
                    if base.kind == CursorKind.CXX_BASE_SPECIFIER:
                        node_data['base_classes'].append(base.type.spelling)

                # Visit children to find methods and members
                for child in node.get_children():
                    if child.kind == CursorKind.CXX_METHOD:
                        method_data = {
                            'type': 'Method',
                            'name': child.spelling,
                            'return_type': child.result_type.spelling,
                            'parameters': [
                                {'name': arg.spelling, 'type': arg.type.spelling}
                                for arg in child.get_arguments()
                            ],
                            'is_virtual': 'virtual' in child.type.spelling,
                            'is_static': child.is_static_method(),
                            'is_const': child.is_const_method()
                        }
                        node_data['methods'].append(method_data)
                    elif child.kind == CursorKind.FIELD_DECL:
                        member_data = {
                            'type': 'Member',
                            'name': child.spelling,
                            'type': child.type.spelling,
                            'is_static': child.is_static_field()
                        }
                        if member_data['is_static']:
                            node_data['static_members'].append(member_data)
                        else:
                            node_data['members'].append(member_data)

                processed_classes[node.spelling] = node_data

            elif node.kind == CursorKind.NAMESPACE:
                # Collect namespace details
                namespace_data = {
                    'type': 'Namespace',
                    'name': node.spelling,
                    'children': []
                }
                for child in node.get_children():
                    namespace_data['children'].append(visit_node(child, depth + 1))
                return namespace_data

            elif node.kind == CursorKind.ENUM_DECL:
                # Collect enum details
                enum_data = {
                    'type': 'Enum',
                    'name': node.spelling,
                    'values': [
                        {'name': enum_value.spelling}
                        for enum_value in node.get_children()
                        if enum_value.kind == CursorKind.ENUM_CONSTANT_DECL
                    ]
                }
                output_data.append(enum_data)

            elif node.kind == CursorKind.TYPEDEF_DECL:
                # Collect typedef details
                typedef_data = {
                    'type': 'Typedef',
                    'name': node.spelling,
                    'underlying_type': node.underlying_typedef_type.spelling
                }
                output_data.append(typedef_data)

            elif node.kind == CursorKind.MACRO_DEFINITION:
                # Collect macro details
                macro_data = {
                    'type': 'Macro',
                    'name': node.spelling,
                    'value': ''.join([t.spelling for t in node.get_tokens() if t.kind == TokenKind.LITERAL])
                }
                output_data.append(macro_data)

            if node_data:
                output_data.append(node_data)

            # Visit children
            for child in node.get_children():
                visit_node(child, depth + 1)

        # Start visiting nodes from the root of the AST
        visit_node(tu.cursor)

    # Process each file
    for file_path in file_paths:
        translation_unit = index.parse(file_path, args=['-x', 'c++', '-std=c++14'])
        process_translation_unit(translation_unit)

    # Consolidate class inheritance
    for class_data in output_data:
        if class_data['type'] == 'Class':
            for base_class in class_data['base_classes']:
                if base_class in processed_classes:
                    base_class_data = processed_classes[base_class]
                    class_data['members'] = base_class_data['members'] + class_data['members']
                    class_data['methods'] = base_class_data['methods'] + class_data['methods']
                    class_data['static_members'] = base_class_data['static_members'] + class_data['static_members']

    return output_data

def save_to_yaml(data, output_file):
    # Write the output data to a YAML file
    with open(output_file, 'w') as file:
        yaml.dump(data, file, sort_keys=False)
