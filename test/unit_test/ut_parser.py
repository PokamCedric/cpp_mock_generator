import unittest
import yaml
import os
from clang.cindex import Index, CursorKind
from parser import (
    initialize_index, process_function, process_class, process_method,
    process_member, process_namespace, process_enum, process_typedef,
    process_macro, parse_header, save_to_yaml, parse_and_save, consolidate_classes
)

class TestParser(unittest.TestCase):

    def setUp(self):
        """Set up the Clang index and mock nodes for testing."""
        self.index = initialize_index()

    def test_process_function(self):
        """Test processing a function declaration."""
        tu = self.index.parse('tests/test_function.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.FUNCTION_DECL:
                function_data = process_function(node)
                self.assertEqual(function_data['type'], 'Function')
                self.assertEqual(function_data['name'], 'testFunction')
                self.assertEqual(function_data['return_type'], 'int')
                self.assertEqual(len(function_data['parameters']), 1)
                self.assertEqual(function_data['parameters'][0]['name'], 'a')
                self.assertEqual(function_data['parameters'][0]['type'], 'int')

    def test_process_class(self):
        """Test processing a class declaration."""
        tu = self.index.parse('tests/test_class.h', args=['-x', 'c++', '-std=c++14'])
        processed_classes = {}
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.CLASS_DECL:
                class_data = process_class(node, processed_classes)
                self.assertEqual(class_data['type'], 'Class')
                self.assertEqual(class_data['name'], 'TestClass')
                self.assertEqual(len(class_data['methods']), 1)
                self.assertEqual(class_data['methods'][0]['name'], 'testMethod')

    def test_process_method(self):
        """Test processing a method declaration."""
        tu = self.index.parse('tests/test_class.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.CLASS_DECL:
                for child in node.get_children():
                    if child.kind == CursorKind.CXX_METHOD:
                        method_data = process_method(child)
                        self.assertEqual(method_data['type'], 'Method')
                        self.assertEqual(method_data['name'], 'testMethod')
                        self.assertEqual(method_data['return_type'], 'void')
                        self.assertEqual(len(method_data['parameters']), 0)

    def test_process_member(self):
        """Test processing a member declaration."""
        tu = self.index.parse('tests/test_class.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.CLASS_DECL:
                for child in node.get_children():
                    if child.kind == CursorKind.FIELD_DECL:
                        member_data = process_member(child)
                        self.assertEqual(member_data['type'], 'Member')
                        self.assertEqual(member_data['name'], 'testMember')
                        self.assertEqual(member_data['type'], 'int')
                        self.assertFalse(member_data['is_static'])

    def test_process_namespace(self):
        """Test processing a namespace declaration."""
        tu = self.index.parse('tests/test_namespace.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.NAMESPACE:
                namespace_data = process_namespace(node)
                self.assertEqual(namespace_data['type'], 'Namespace')
                self.assertEqual(namespace_data['name'], 'TestNamespace')

    def test_process_enum(self):
        """Test processing an enum declaration."""
        tu = self.index.parse('tests/test_enum.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.ENUM_DECL:
                enum_data = process_enum(node)
                self.assertEqual(enum_data['type'], 'Enum')
                self.assertEqual(enum_data['name'], 'TestEnum')
                self.assertEqual(len(enum_data['values']), 2)

    def test_process_enum_class(self):
        """Test processing an enum class declaration."""
        tu = self.index.parse('tests/test_enum_class.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.ENUM_DECL:
                enum_data = process_enum(node)
                self.assertEqual(enum_data['type'], 'EnumClass')
                self.assertEqual(enum_data['name'], 'TestEnumClass')
                self.assertEqual(len(enum_data['values']), 2)

    def test_process_typedef(self):
        """Test processing a typedef declaration."""
        tu = self.index.parse('tests/test_typedef.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.TYPEDEF_DECL:
                typedef_data = process_typedef(node)
                self.assertEqual(typedef_data['type'], 'Typedef')
                self.assertEqual(typedef_data['name'], 'TestType')
                self.assertEqual(typedef_data['underlying_type'], 'int')

    def test_process_macro(self):
        """Test processing a macro definition."""
        tu = self.index.parse('tests/test_macro.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.MACRO_DEFINITION:
                macro_data = process_macro(node)
                self.assertEqual(macro_data['type'], 'Macro')
                self.assertEqual(macro_data['name'], 'TEST_MACRO')
                self.assertEqual(macro_data['value'], '1')

    def test_parse_header(self):
        """Test parsing a header file."""
        parsed_data = parse_header(['tests/test_function.h'])
        self.assertEqual(len(parsed_data), 1)
        self.assertEqual(parsed_data[0]['type'], 'Function')
        self.assertEqual(parsed_data[0]['name'], 'testFunction')

    def test_save_to_yaml(self):
        """Test saving parsed data to a YAML file."""
        data = {'type': 'Test', 'name': 'test'}
        output_file = 'tests/test_output.yaml'
        save_to_yaml(data, output_file)
        with open(output_file, 'r') as file:
            loaded_data = yaml.safe_load(file)
        self.assertEqual(loaded_data, data)
        os.remove(output_file)

    def test_parse_and_save(self):
        """Test parsing a header file and saving the result to a YAML file."""
        output_directory = 'tests/outputs'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        output_file = parse_and_save('tests/test_function.h', output_directory)
        with open(output_file, 'r') as file:
            loaded_data = yaml.safe_load(file)
        self.assertEqual(len(loaded_data), 1)
        self.assertEqual(loaded_data[0]['type'], 'Function')
        self.assertEqual(loaded_data[0]['name'], 'testFunction')
        os.remove(output_file)

    def test_consolidate_classes(self):
        """Test consolidating class inheritance."""
        base_class = {
            'type': 'Class',
            'name': 'BaseClass',
            'base_classes': [],
            'members': [{'name': 'baseMember', 'type': 'int', 'is_static': False}],
            'methods': [{'name': 'baseMethod', 'return_type': 'void', 'parameters': [], 'is_virtual': False, 'is_static': False, 'is_const': False}],
            'static_members': []
        }

        derived_class = {
            'type': 'Class',
            'name': 'DerivedClass',
            'base_classes': ['BaseClass'],
            'members': [{'name': 'derivedMember', 'type': 'int', 'is_static': False}],
            'methods': [{'name': 'derivedMethod', 'return_type': 'void', 'parameters': [], 'is_virtual': False, 'is_static': False, 'is_const': False}],
            'static_members': []
        }

        processed_classes = {
            'BaseClass': base_class,
            'DerivedClass': derived_class
        }

        output_data = [base_class, derived_class]
        consolidate_classes(output_data, processed_classes)

        # After consolidation, the derived class should have members and methods from the base class
        self.assertEqual(len(output_data[1]['members']), 2)  # baseMember + derivedMember
        self.assertEqual(len(output_data[1]['methods']), 2)  # baseMethod + derivedMethod

    def test_parse_base_class(self):
        """Test parsing of BaseClass."""
        tu = self.index.parse('tests/test_class.h', args=['-x', 'c++', '-std=c++14'])
        base_class_data = None
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.CLASS_DECL and node.spelling == 'BaseClass':
                base_class_data = process_class(node, {})
                break

        self.assertIsNotNone(base_class_data)
        self.assertEqual(base_class_data['type'], 'Class')
        self.assertEqual(base_class_data['name'], 'BaseClass')
        self.assertIn('methods', base_class_data)
        self.assertIn('members', base_class_data)
        self.assertIn('static_members', base_class_data)
        self.assertIn('friend_classes', base_class_data)
        self.assertEqual(len(base_class_data['methods']), 1)  # Only publicMethod
        self.assertEqual(len(base_class_data['members']), 1)  # Only privateMember
        self.assertEqual(len(base_class_data['static_members']), 0)  # No static members
        self.assertIn('FriendClass', base_class_data['friend_classes'])

    def test_parse_derived_class(self):
        """Test parsing of DerivedClass."""
        tu = self.index.parse('tests/test_class.h', args=['-x', 'c++', '-std=c++14'])
        derived_class_data = None
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.CLASS_DECL and node.spelling == 'DerivedClass':
                derived_class_data = process_class(node, {})
                break

        self.assertIsNotNone(derived_class_data)
        self.assertEqual(derived_class_data['type'], 'Class')
        self.assertEqual(derived_class_data['name'], 'DerivedClass')
        self.assertIn('methods', derived_class_data)
        self.assertIn('members', derived_class_data)
        self.assertIn('static_members', derived_class_data)
        self.assertIn('friend_classes', derived_class_data)
        self.assertEqual(len(derived_class_data['methods']), 1)  # Only derivedPublicMethod
        self.assertEqual(len(derived_class_data['members']), 1)  # Only derivedPrivateMethod
        self.assertEqual(len(derived_class_data['static_members']), 0)  # No static members
        self.assertIn('FriendClass', derived_class_data['friend_classes'])

    def test_parse_friend_class(self):
        """Test parsing of FriendClass."""
        tu = self.index.parse('tests/test_class.h', args=['-x', 'c++', '-std=c++14'])
        friend_class_data = None
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.CLASS_DECL and node.spelling == 'FriendClass':
                friend_class_data = process_class(node, {})
                break

        self.assertIsNotNone(friend_class_data)
        self.assertEqual(friend_class_data['type'], 'Class')
        self.assertEqual(friend_class_data['name'], 'FriendClass')
        self.assertIn('methods', friend_class_data)
        self.assertIn('members', friend_class_data)
        self.assertIn('static_members', friend_class_data)
        self.assertNotIn('friend_classes', friend_class_data)  # Friend class shouldn't list friend classes
        self.assertEqual(len(friend_class_data['methods']), 2)  # friendMethod for BaseClass and DerivedClass
        self.assertEqual(len(friend_class_data['members']), 0)  # No members
        self.assertEqual(len(friend_class_data['static_members']), 0)  # No static members

    def test_save_to_yaml(self):
        """Test saving data to YAML."""
        data = {
            'type': 'Class',
            'name': 'Test',
            'methods': [{'name': 'method1', 'return_type': 'void', 'parameters': []}],
            'members': [],
            'static_members': [],
            'friend_classes': []
        }
        save_to_yaml(data, 'tests/test_output.yaml')

        # Check if the file was created
        self.assertTrue(os.path.exists('tests/test_output.yaml'))

        # Load YAML and check if data matches
        with open('tests/test_output.yaml', 'r') as file:
            loaded_data = yaml.safe_load(file)

        self.assertEqual(loaded_data['type'], 'Class')
        self.assertEqual(loaded_data['name'], 'Test')
        self.assertEqual(len(loaded_data['methods']), 1)
        self.assertEqual(loaded_data['methods'][0]['name'], 'method1')


if __name__ == '__main__':
    unittest.main()
