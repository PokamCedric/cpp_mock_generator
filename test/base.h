// base.h
#ifndef BASE_H
#define BASE_H

#include <string>

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

#endif // BASE_H
