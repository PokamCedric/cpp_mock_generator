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
        """
        **Test Name:** `test_process_function`

        **Purpose:**
        To verify that the `process_function` correctly processes a function declaration node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing a function declaration.

        **Execution:**
        1. Traverse the parsed nodes and identify the function declaration node.
        2. Call `process_function` on the identified function node.

        **Validation:**
        1. Verify that the processed function data:
           - Type is 'Function'.
           - Name is 'testFunction'.
           - Return type is 'int'.
           - Has one parameter named 'a' of type 'int'.
        """
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
        """
        **Test Name:** `test_process_class`

        **Purpose:**
        To verify that the `process_class` correctly processes a class declaration node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing a class declaration.

        **Execution:**
        1. Traverse the parsed nodes and identify the class declaration node.
        2. Call `process_class` on the identified class node.

        **Validation:**
        1. Verify that the processed class data:
           - Type is 'Class'.
           - Name is 'TestClass'.
           - Has one method named 'testMethod'.
        """
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
        """
        **Test Name:** `test_process_method`

        **Purpose:**
        To verify that the `process_method` correctly processes a method declaration node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing a class with a method.

        **Execution:**
        1. Traverse the parsed nodes to find the class declaration node.
        2. Within the class node, identify the method declaration node.
        3. Call `process_method` on the identified method node.

        **Validation:**
        1. Verify that the processed method data:
           - Type is 'Method'.
           - Name is 'testMethod'.
           - Return type is 'void'.
           - Has no parameters.
        """
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
        """
        **Test Name:** `test_process_member`

        **Purpose:**
        To verify that the `process_member` correctly processes a member declaration node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing a class with a member.

        **Execution:**
        1. Traverse the parsed nodes to find the class declaration node.
        2. Within the class node, identify the member declaration node.
        3. Call `process_member` on the identified member node.

        **Validation:**
        1. Verify that the processed member data:
           - Type is 'Member'.
           - Name is 'testMember'.
           - Type is 'int'.
           - Is not static.
        """
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
        """
        **Test Name:** `test_process_namespace`

        **Purpose:**
        To verify that the `process_namespace` correctly processes a namespace declaration node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing a namespace.

        **Execution:**
        1. Traverse the parsed nodes and identify the namespace declaration node.
        2. Call `process_namespace` on the identified namespace node.

        **Validation:**
        1. Verify that the processed namespace data:
           - Type is 'Namespace'.
           - Name is 'TestNamespace'.
        """
        tu = self.index.parse('tests/test_namespace.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.NAMESPACE:
                namespace_data = process_namespace(node)
                self.assertEqual(namespace_data['type'], 'Namespace')
                self.assertEqual(namespace_data['name'], 'TestNamespace')

    def test_process_enum(self):
        """
        **Test Name:** `test_process_enum`

        **Purpose:**
        To verify that the `process_enum` correctly processes an enum declaration node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing an enum.

        **Execution:**
        1. Traverse the parsed nodes and identify the enum declaration node.
        2. Call `process_enum` on the identified enum node.

        **Validation:**
        1. Verify that the processed enum data:
           - Type is 'Enum'.
           - Name is 'TestEnum'.
           - Has two values.
        """
        tu = self.index.parse('tests/test_enum.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.ENUM_DECL:
                enum_data = process_enum(node)
                self.assertEqual(enum_data['type'], 'Enum')
                self.assertEqual(enum_data['name'], 'TestEnum')
                self.assertEqual(len(enum_data['values']), 2)

    def test_process_enum_class(self):
        """
        **Test Name:** `test_process_enum_class`

        **Purpose:**
        To verify that the `process_enum` correctly processes an enum class declaration node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing an enum class.

        **Execution:**
        1. Traverse the parsed nodes and identify the enum class declaration node.
        2. Call `process_enum` on the identified enum class node.

        **Validation:**
        1. Verify that the processed enum class data:
           - Type is 'EnumClass'.
           - Name is 'TestEnumClass'.
           - Has two values.
        """
        tu = self.index.parse('tests/test_enum_class.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.ENUM_DECL:
                enum_data = process_enum(node)
                self.assertEqual(enum_data['type'], 'EnumClass')
                self.assertEqual(enum_data['name'], 'TestEnumClass')
                self.assertEqual(len(enum_data['values']), 2)

    def test_process_typedef(self):
        """
        **Test Name:** `test_process_typedef`

        **Purpose:**
        To verify that the `process_typedef` correctly processes a typedef declaration node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing a typedef.

        **Execution:**
        1. Traverse the parsed nodes and identify the typedef declaration node.
        2. Call `process_typedef` on the identified typedef node.

        **Validation:**
        1. Verify that the processed typedef data:
           - Type is 'Typedef'.
           - Name is 'TestType'.
           - Underlying type is 'int'.
        """
        tu = self.index.parse('tests/test_typedef.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.TYPEDEF_DECL:
                typedef_data = process_typedef(node)
                self.assertEqual(typedef_data['type'], 'Typedef')
                self.assertEqual(typedef_data['name'], 'TestType')
                self.assertEqual(typedef_data['underlying_type'], 'int')

    def test_process_macro(self):
        """
        **Test Name:** `test_process_macro`

        **Purpose:**
        To verify that the `process_macro` correctly processes a macro definition node and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing a macro definition.

        **Execution:**
        1. Traverse the parsed nodes and identify the macro definition node.
        2. Call `process_macro` on the identified macro node.

        **Validation:**
        1. Verify that the processed macro data:
           - Type is 'Macro'.
           - Name is 'TEST_MACRO'.
           - Value is '1'.
        """
        tu = self.index.parse('tests/test_macro.h', args=['-x', 'c++', '-std=c++14'])
        for node in tu.cursor.get_children():
            if node.kind == CursorKind.MACRO_DEFINITION:
                macro_data = process_macro(node)
                self.assertEqual(macro_data['type'], 'Macro')
                self.assertEqual(macro_data['name'], 'TEST_MACRO')
                self.assertEqual(macro_data['value'], '1')

    def test_parse_header(self):
        """
        **Test Name:** `test_parse_header`

        **Purpose:**
        To verify that the `parse_header` correctly parses a header file and extracts the appropriate data structure.

        **Setup:**
        1. Initialize Clang index and parse a test header file.

        **Execution:**
        1. Call `parse_header` on the test header file.

        **Validation:**
        1. Verify that the parsed data contains:
           - One function with type 'Function'.
           - Name 'testFunction'.
        """
        parsed_data = parse_header(['tests/test_function.h'])
        self.assertEqual(len(parsed_data), 1)
        self.assertEqual(parsed_data[0]['type'], 'Function')
        self.assertEqual(parsed_data[0]['name'], 'testFunction')

    def test_save_to_yaml(self):
        """
        **Test Name:** `test_save_to_yaml`

        **Purpose:**
        To verify that the `save_to_yaml` function correctly saves a given data structure to a YAML file and that the saved data matches the original data.

        **Setup:**
        1. Define a dictionary `data` containing:
           - A type of 'Class'.
           - A name 'Test'.
           - One method named 'method1' with a return type of 'void' and no parameters.
           - Empty lists for members, static members, and friend classes.

        **Execution:**
        1. Call the `save_to_yaml` function with `data` and the file path `'tests/test_output.yaml'`.

        **Validation:**
        1. Verify that the file `tests/test_output.yaml` is created successfully.
        2. Load the contents of the file `tests/test_output.yaml` using `yaml.safe_load`.
        3. Assert that the loaded data matches the original data structure by checking:
           - The value of the 'type' key is 'Class'.
           - The value of the 'name' key is 'Test'.
           - The length of the 'methods' list is 1.
           - The name of the first method in the 'methods' list is 'method1'.
        """
        data = {
            'type': 'Class',
            'name': 'Test',
            'methods': [{'name': 'method1', 'return_type': 'void', 'parameters': []}],
            'members': [],
            'static_members': [],
            'friend_classes': []
        }
        output_file = 'tests/test_output.yaml'
        save_to_yaml(data, output_file)
        with open(output_file, 'r') as file:
            loaded_data = yaml.safe_load(file)
        self.assertEqual(loaded_data, data)
        os.remove(output_file)

    def test_parse_and_save(self):
        """
        **Test Name:** `test_parse_and_save`

        **Purpose:**
        To verify that the `parse_and_save` function correctly parses a header file and saves the resulting data structure to a YAML file.

        **Setup:**
        1. Specify the test header file `tests/test_function.h`.
        2. Specify the output directory `tests/outputs`.

        **Execution:**
        1. Call `parse_and_save` with the test header file and output directory.

        **Validation:**
        1. Verify that the YAML file is created successfully in the specified output directory.
        2. Load the contents of the YAML file using `yaml.safe_load`.
        3. Assert that the loaded data contains:
           - One function with type 'Function'.
           - Name 'testFunction'.

        **Cleanup:**
        Remove the output file
        """
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
        """
        **Test Name:** `test_consolidate_classes`

        **Purpose:**
        To verify that the `consolidate_classes` function correctly consolidates class inheritance by combining members and methods from base classes into derived classes.

        **Setup:**
        1. Define a dictionary `base_class` representing the base class with:
           - Type 'Class'.
           - Name 'BaseClass'.
           - One member named 'baseMember' of type 'int' and not static.
           - One method named 'baseMethod' with return type 'void', no parameters, not virtual, not static, and not const.
           - No static members.
        2. Define a dictionary `derived_class` representing the derived class with:
           - Type 'Class'.
           - Name 'DerivedClass'.
           - Base class 'BaseClass'.
           - One member named 'derivedMember' of type 'int' and not static.
           - One method named 'derivedMethod' with return type 'void', no parameters, not virtual, not static, and not const.
           - No static members.
        3. Define a dictionary `processed_classes` containing both `base_class` and `derived_class`.
        4. Define a list `output_data` containing both `base_class` and `derived_class`.

        **Execution:**
        1. Call `consolidate_classes` with `output_data` and `processed_classes`.

        **Validation:**
        1. Verify that the derived class now includes members and methods from the base class by checking:
           - The derived class contains 2 members (baseMember and derivedMember).
           - The derived class contains 2 methods (baseMethod and derivedMethod).
        """
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

        self.assertEqual(len(output_data[1]['members']), 2)  # baseMember + derivedMember
        self.assertEqual(len(output_data[1]['methods']), 2)  # baseMethod + derivedMethod

    def test_parse_base_class(self):
        """
        **Test Name:** `test_parse_base_class`

        **Purpose:**
        To verify that the `process_class` correctly parses a base class and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing the class 'BaseClass'.

        **Execution:**
        1. Traverse the parsed nodes and identify the class declaration node for 'BaseClass'.
        2. Call `process_class` on the identified class node.

        **Validation:**
        1. Verify that the parsed class data:
           - Type is 'Class'.
           - Name is 'BaseClass'.
           - Contains methods, members, static members, and friend classes.
           - Has 1 method named 'publicMethod'.
           - Has 1 member named 'privateMember'.
           - Has no static members.
           - Lists 'FriendClass' as a friend class.
        """
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
        """
        **Test Name:** `test_parse_derived_class`

        **Purpose:**
        To verify that the `process_class` correctly parses a derived class and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing the class 'DerivedClass'.

        **Execution:**
        1. Traverse the parsed nodes and identify the class declaration node for 'DerivedClass'.
        2. Call `process_class` on the identified class node.

        **Validation:**
        1. Verify that the parsed class data:
           - Type is 'Class'.
           - Name is 'DerivedClass'.
           - Contains methods, members, static members, and friend classes.
           - Has 1 method named 'derivedPublicMethod'.
           - Has 1 member named 'derivedPrivateMember'.
           - Has no static members.
           - Lists 'FriendClass' as a friend class.
        """
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
        """
        **Test Name:** `test_parse_friend_class`

        **Purpose:**
        To verify that the `process_class` correctly parses a friend class and extracts the appropriate details.

        **Setup:**
        1. Initialize Clang index and parse a test header file containing the class 'FriendClass'.

        **Execution:**
        1. Traverse the parsed nodes and identify the class declaration node for 'FriendClass'.
        2. Call `process_class` on the identified class node.

        **Validation:**
        1. Verify that the parsed class data:
           - Type is 'Class'.
           - Name is 'FriendClass'.
           - Contains methods, members, and static members.
           - Does not list friend classes.
           - Has 2 methods (friendMethod for BaseClass and DerivedClass).
           - Has no members.
           - Has no static members.
        """
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
        """
        **Test Name:** `test_save_to_yaml`

        **Purpose:**
        To verify that the `save_to_yaml` function correctly saves a given data structure to a YAML file and that the saved data matches the original data.

        **Setup:**
        1. Define a dictionary `data` containing:
           - A type of 'Class'.
           - A name 'Test'.
           - One method named 'method1' with a return type of 'void' and no parameters.
           - Empty lists for members, static members, and friend classes.

        **Execution:**
        1. Call the `save_to_yaml` function with `data` and the file path `'tests/test_output.yaml'`.

        **Validation:**
        1. Verify that the file `tests/test_output.yaml` is created successfully.
        2. Load the contents of the file `tests/test_output.yaml` using `yaml.safe_load`.
        3. Assert that the loaded data matches the original data structure by checking:
           - The value of the 'type' key is 'Class'.
           - The value of the 'name' key is 'Test'.
           - The length of the 'methods' list is 1.
           - The name of the first method in the 'methods' list is 'method1'.
        """
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
