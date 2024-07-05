// test.h
#ifndef TEST_H
#define TEST_H

#include <string>

class Person {
public:
    Person(const std::string &name, int age);
    virtual ~Person();

    std::string getName() const;
    int getAge() const;

    virtual void displayInfo() const;

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

#endif // TEST_H
