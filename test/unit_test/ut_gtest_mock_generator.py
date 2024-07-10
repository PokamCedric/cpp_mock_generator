import unittest
import os
from cppparser import CppParser
from gtest_mock_generator import GMockGenerator

class TestGMockGenerator(unittest.TestCase):
    def setUp(self):
        self.parser = CppParser()
        self.generator = GMockGenerator()

        self.test_header_content = """
class FriendClass;

class BaseClass {
public:
    BaseClass() {}

    void publicMethod() {}

protected:
    int protectedMember;

    void protectedMethod() {}

private:
    double privateMember;

    void privateMethod() {}

    friend class FriendClass;
};

class DerivedClass : public BaseClass {
public:
    DerivedClass() {}

    void derivedPublicMethod() {}

protected:
    void derivedProtectedMethod() {}

private:
    void derivedPrivateMethod() {}

    friend class FriendClass;
};

class FriendClass {
public:
    FriendClass() {}

    void friendMethod(BaseClass& base) {
        base.privateMethod();  // Accessing private method of BaseClass
    }

    void friendMethod(DerivedClass& derived) {
        derived.derivedPrivateMethod();  // Accessing private method of DerivedClass
    }
};
"""

        self.expected_mock_content = """
#ifndef MOCK_TEST_CLASS_H
#define MOCK_TEST_CLASS_H

#include <gmock/gmock.h>

class MockBaseClass : public BaseClass {
public:
    MOCK_METHOD(void, publicMethod, (), (override));
};

class MockDerivedClass : public DerivedClass {
public:
    MOCK_METHOD(void, derivedPublicMethod, (), (override));
};

class MockFriendClass : public FriendClass {
public:
    MOCK_METHOD(void, friendMethod, (BaseClass& base), (override));
    MOCK_METHOD(void, friendMethod, (DerivedClass& derived), (override));
};

#endif // MOCK_TEST_CLASS_H
"""

    def create_test_header_file(self):
        test_dir = 'tests'
        header_path = os.path.join(test_dir, 'test_class.h')
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        with open(header_path, 'w') as f:
            f.write(self.test_header_content)
        return header_path

    def test_generate_mock_file(self):
        header_path = self.create_test_header_file()
        parsed_data = self.parser.parse_header([header_path])

        output_file = 'tests/MockOutput.h'
        self.generator.generate_mock_file(parsed_data, output_file)

        with open(output_file, 'r') as f:
            generated_mock_content = f.read()

        self.assertEqual(generated_mock_content.strip(), self.expected_mock_content.strip())

if __name__ == '__main__':
    unittest.main()
