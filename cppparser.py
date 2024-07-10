import clang.cindex
from clang.cindex import Index, CursorKind, TokenKind

clang.cindex.Config.set_library_file('C:/LLVM/bin/libclang.dll')

class CppParser:
    def __init__(self):
        self.index = self.__initialize_index()
        self.processed_classes = {}
        self.node_processors = {
            CursorKind.FUNCTION_DECL: self.__process_function,
            CursorKind.CLASS_DECL: self.__process_class,
            CursorKind.NAMESPACE: self.__process_namespace,
            CursorKind.ENUM_DECL: self.__process_enum,
            CursorKind.TYPEDEF_DECL: self.__process_typedef,
            CursorKind.MACRO_DEFINITION: self.__process_macro
        }

    def __initialize_index(self):
        """Initialize the Clang index."""
        return Index.create()

    def __process_function(self, node):
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

    def __process_class(self, node):
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
                method_data = self.__process_method(child)
                class_data['methods'].append(method_data)
            elif child.kind == CursorKind.FIELD_DECL:
                member_data = self.__process_member(child)
                if member_data['is_static']:
                    class_data['static_members'].append(member_data)
                else:
                    class_data['members'].append(member_data)

        self.processed_classes[node.spelling] = class_data
        return class_data

    def __process_method(self, node):
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
            'is_const': node.is_const_method(),
            'access': self.__get_access_specifier(node)
        }

    def __get_access_specifier(self, node):
        """Get the access specifier of a node."""
        access_specifier = node.access_specifier
        if access_specifier == clang.cindex.AccessSpecifier.PUBLIC:
            return 'public'
        elif access_specifier == clang.cindex.AccessSpecifier.PROTECTED:
            return 'protected'
        elif access_specifier == clang.cindex.AccessSpecifier.PRIVATE:
            return 'private'
        else:
            return 'public'  # default to public if unknown

    def __process_member(self, node):
        """Process a member declaration."""
        return {
            'type': 'Member',
            'name': node.spelling,
            'is_static': node.is_static_field(),
            'access': self.__get_access_specifier(node)
        }

    def __process_namespace(self, node):
        """Process a namespace declaration."""
        namespace_data = {
            'type': 'Namespace',
            'name': node.spelling,
            'children': []
        }
        for child in node.get_children():
            child_data = self.__process_node(child)
            if child_data:
                namespace_data['children'].append(child_data)
        return namespace_data

    def __process_enum(self, node):
        """Process an enum declaration."""
        enum_data = {
            'type': 'Enum',
            'name': node.spelling,
            'values': []
        }

        if node.is_scoped_enum():
            enum_data['type'] = 'EnumClass'

        for enum_value in node.get_children():
            if enum_value.kind == CursorKind.ENUM_CONSTANT_DECL:
                enum_data['values'].append({
                    'name': enum_value.spelling
                })

        return enum_data

    def __process_typedef(self, node):
        """Process a typedef declaration."""
        return {
            'type': 'Typedef',
            'name': node.spelling,
            'underlying_type': node.underlying_typedef_type.spelling
        }

    def __process_macro(self, node):
        """Process a macro definition."""
        return {
            'type': 'Macro',
            'name': node.spelling,
            'value': ''.join([t.spelling for t in node.get_tokens() if t.kind == TokenKind.LITERAL])
        }

    def __process_node(self, node):
        """Process a generic AST node."""
        processor = self.node_processors.get(node.kind)
        if processor:
            if node.kind == CursorKind.CLASS_DECL:
                return processor(node)
            return processor(node)
        return None

    def __consolidate_classes(self, output_data):
        """Consolidate class inheritance in the output data."""
        for class_data in output_data:
            if class_data['type'] == 'Class':
                for base_class in class_data['base_classes']:
                    if base_class in self.processed_classes:
                        base_class_data = self.processed_classes[base_class]
                        class_data['members'] = base_class_data['members'] + class_data['members']
                        class_data['methods'] = base_class_data['methods'] + class_data['methods']
                        class_data['static_members'] = base_class_data['static_members'] + class_data['static_members']

    def parse_header(self, file_paths):
        """Parse the header files and extract relevant information."""
        output_data = []

        def process_translation_unit(tu):
            for node in tu.cursor.get_children():
                node_data = self.__process_node(node)
                if node_data:
                    output_data.append(node_data)

        for file_path in file_paths:
            tu = self.index.parse(file_path, args=['-x', 'c++', '-std=c++14'])
            process_translation_unit(tu)

        self.__consolidate_classes(output_data)
        return output_data
