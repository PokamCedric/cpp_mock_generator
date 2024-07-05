import clang.cindex

def parse_header(file_path):
    # Initialize the Clang index
    index = clang.cindex.Index.create()

    # Parse the header file
    translation_unit = index.parse(file_path, args=['-x', 'c++', '-std=c++14'])

    # Function to recursively visit nodes in the AST
    def visit_node(node, depth=0):
        indent = '  ' * depth

        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            # Print function details in YAML-like format
            print(f'{indent}Function:')
            print(f'{indent}  Name: {node.spelling}')
            print(f'{indent}  Return Type: {node.result_type.spelling}')
            print(f'{indent}  Parameters:')
            for arg in node.get_arguments():
                print(f'{indent}    - Name: {arg.spelling}')
                print(f'{indent}      Type: {arg.type.spelling}')
            print()

        elif node.kind in (clang.cindex.CursorKind.CLASS_DECL, clang.cindex.CursorKind.STRUCT_DECL):
            # Print class or struct details in YAML-like format
            print(f'{indent}{"Class" if node.kind == clang.cindex.CursorKind.CLASS_DECL else "Struct"}:')
            print(f'{indent}  Name: {node.spelling}')
            print(f'{indent}  Members and Methods:')
            # Visit children to find methods and members
            for child in node.get_children():
                if child.kind == clang.cindex.CursorKind.CXX_METHOD:
                    print(f'{indent}    Method:')
                    print(f'{indent}      Name: {child.spelling}')
                    print(f'{indent}      Return Type: {child.result_type.spelling}')
                    print(f'{indent}      Parameters:')
                    for arg in child.get_arguments():
                        print(f'{indent}        - Name: {arg.spelling}')
                        print(f'{indent}          Type: {arg.type.spelling}')
                elif child.kind == clang.cindex.CursorKind.FIELD_DECL:
                    print(f'{indent}    Member:')
                    print(f'{indent}      Name: {child.spelling}')
                    print(f'{indent}      Type: {child.type.spelling}')
            print()

        # Visit children
        for child in node.get_children():
            visit_node(child, depth + 1)

    # Start visiting nodes from the root of the AST
    visit_node(translation_unit.cursor)

# Example usage
if __name__ == '__main__':
    header_file = 'example.h'  # Remplacez par le chemin de votre fichier d'en-tête
    parse_header(header_file)
