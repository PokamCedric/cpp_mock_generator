class GMockGenerator:
    def generate_mock_file(self, parsed_data, output_file):
        header_guard = self.__generate_header_guard(output_file)
        mocks = []
        for item in parsed_data:
            if item['type'] == 'Class':
                mocks.append(self.__generate_class_mock(item))

        with open(output_file, 'w') as f:
            f.write(f"#ifndef {header_guard}\n")
            f.write(f"#define {header_guard}\n\n")
            f.write('#include <gmock/gmock.h>\n\n')
            f.write('\n\n'.join(mocks))
            f.write(f"\n\n#endif // {header_guard}\n")

    def __generate_class_mock(self, class_data):
        class_name = class_data['name']
        mock_class_name = f'Mock{class_name}'
        mock_methods = [self.__generate_method_mock(method) for method in class_data['methods']]

        mock_class = f"class {mock_class_name} : public {class_name} {{\npublic:\n"
        mock_class += '\n'.join(mock_methods)
        mock_class += "\n};"

        return mock_class

    def __generate_method_mock(self, method_data):
        method_name = method_data['name']
        return_type = method_data['return_type']
        params = ', '.join([f"{param['type']} {param['name']}" for param in method_data['parameters']])
        return f"    MOCK_METHOD({return_type}, {method_name}, ({params}), (override));"

    def __generate_header_guard(self, file_path):
        base_name = os.path.basename(file_path).replace('.', '_').upper()
        return f"MOCK_{base_name}"

# Usage example:
# Assume `parser` is an instance of `CppParser` and `parsed_data` is obtained by calling `parser.parse_header(["path_to_header.h"])`.

parser = CppParser()
parsed_data = parser.parse_header(['path_to_header.h'])
mock_generator = GMockGenerator()
mock_generator.generate_mock_file(parsed_data, 'MockOutput.h')
