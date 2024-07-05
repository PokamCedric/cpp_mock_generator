// test.h
#ifndef TEST_H
#define TEST_H

#include <string>

#define PI 3.14159  // Define a constant

namespace MathUtils {
    template <typename T>
    T add(T a, T b) {
        return a + b;
    }
}

using String = std::string;  // Type alias

enum Color {
    RED,
    GREEN,
    BLUE
};

class Person {
public:
    Person(const std::string &name, int age);
    virtual ~Person();

    std::string getName() const;
    int getAge() const;

    virtual void displayInfo() const;

    static int population;  // Static member variable

private:
    std::string name;
    int age;
};

class Student : public Person {
public:
    Student(const std::string &name, int age, int studentID);
    ~Student();

    int getStudentID() const;
    void displayInfo() const override;

private:
    int studentID;
};

int add(int a, int b);
void print_message(const char* message);
double multiply(double x, double y);

#endif // TEST_H
