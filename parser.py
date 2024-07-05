import yaml
from clang.cindex import Config, Index, CursorKind, TokenKind

# Set the library path for libclang
Config.set_library_path('/usr/lib/llvm-13/lib')

def initialize_index():
    """Initialize the Clang index."""
    return Index.create()

def process_function(node):
    """Process a function declaration."""
    return {
        'type': 'Function',
        'name': node.spelling,
        'return_type': node.result_type.spelling,
        'parameters': [
            {'name': arg.spelling, 'type': arg.type.spelling}
            for arg in node.get_arguments()
        ]
    }

def process_class(node, processed_classes):
    """Process a class declaration."""
    class_data = {
        'type': 'Class',
        'name': node.spelling,
        'base_classes': [],
        'members': [],
        'methods': [],
        'static_members': []
    }

    for base in node.get_children():
        if base.kind == CursorKind.CXX_BASE_SPECIFIER:
            class_data['base_classes'].append(base.type.spelling)

    for child in node.get_children():
        if child.kind == CursorKind.CXX_METHOD:
            method_data = process_method(child)
            class_data['methods'].append(method_data)
        elif child.kind == CursorKind.FIELD_DECL:
            member_data = process_member(child)
            if member_data['is_static']:
                class_data['static_members'].append(member_data)
            else:
                class_data['members'].append(member_data)

    processed_classes[node.spelling] = class_data
    return class_data

def process_method(node):
    """Process a method declaration."""
    return {
        'type': 'Method',
        'name': node.spelling,
        'return_type': node.result_type.spelling,
        'parameters': [
            {'name': arg.spelling, 'type': arg.type.spelling}
            for arg in node.get_arguments()
        ],
        'is_virtual': 'virtual' in node.type.spelling,
        'is_static': node.is_static_method(),
        'is_const': node.is_const_method()
    }

def process_member(node):
    """Process a member declaration."""
    return {
        'type': 'Member',
        'name': node.spelling,
        'type': node.type.spelling,
        'is_static': node.is_static_field()
    }

def process_namespace(node):
    """Process a namespace declaration."""
    namespace_data = {
        'type': 'Namespace',
        'name': node.spelling,
        'children': []
    }
    for child in node.get_children():
        namespace_data['children'].append(process_node(child))
    return namespace_data

def process_enum(node):
    """Process an enum declaration."""
    return {
        'type': 'Enum',
        'name': node.spelling,
        'values': [
            {'name': enum_value.spelling}
            for enum_value in node.get_children()
            if enum_value.kind == CursorKind.ENUM_CONSTANT_DECL
        ]
    }

def process_typedef(node):
    """Process a typedef declaration."""
    return {
        'type': 'Typedef',
        'name': node.spelling,
        'underlying_type': node.underlying_typedef_type.spelling
    }

def process_macro(node):
    """Process a macro definition."""
    return {
        'type': 'Macro',
        'name': node.spelling,
        'value': ''.join([t.spelling for t in node.get_tokens() if t.kind == TokenKind.LITERAL])
    }

def process_node(node):
    """Process a generic AST node."""
    if node.kind == CursorKind.FUNCTION_DECL and not node.semantic_parent.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
        return process_function(node)
    elif node.kind == CursorKind.CLASS_DECL:
        return process_class(node, processed_classes)
    elif node.kind == CursorKind.NAMESPACE:
        return process_namespace(node)
    elif node.kind == CursorKind.ENUM_DECL:
        return process_enum(node)
    elif node.kind == CursorKind.TYPEDEF_DECL:
        return process_typedef(node)
    elif node.kind == CursorKind.MACRO_DEFINITION:
        return process_macro(node)
    return None

def consolidate_classes(output_data, processed_classes):
    """Consolidate class inheritance in the output data."""
    for class_data in output_data:
        if class_data['type'] == 'Class':
            for base_class in class_data['base_classes']:
                if base_class in processed_classes:
                    base_class_data = processed_classes[base_class]
                    class_data['members'] = base_class_data['members'] + class_data['members']
                    class_data['methods'] = base_class_data['methods'] + class_data['methods']
                    class_data['static_members'] = base_class_data['static_members'] + class_data['static_members']

def parse_header(file_paths):
    """Parse the header files and extract relevant information."""
    index = initialize_index()

    output_data = []
    global processed_classes
    processed_classes = {}

    def process_translation_unit(tu):
        for node in tu.cursor.get_children():
            node_data = process_node(node)
            if node_data:
                output_data.append(node_data)

    for file_path in file_paths:
        tu = index.parse(file_path, args=['-x', 'c++', '-std=c++14'])
        process_translation_unit(tu)

    consolidate_classes(output_data, processed_classes)

    return output_data

def save_to_yaml(data, output_file):
    """Save the parsed data to a YAML file."""
    with open(output_file, 'w') as file:
        yaml.dump(data, file, sort_keys=False)
