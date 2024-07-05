#ifndef EXAMPLE_H
#define EXAMPLE_H

int add(int a, int b);
void print_message(const char* message);
double multiply(double x, double y);

class ExampleClass {
public:
    ExampleClass();
    ~ExampleClass();
    int exampleMethod(int param1, double param2);
private:
    int memberVariable;
};

struct ExampleStruct {
    int field1;
    double field2;
    void structMethod();
};

#endif // EXAMPLE_H

