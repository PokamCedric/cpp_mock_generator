// derived.h
#ifndef DERIVED_H
#define DERIVED_H

#include "base.h"

class Student : public Person {
public:
    Student(const std::string &name, int age, int studentID);
    ~Student();

    int getStudentID() const;
    void displayInfo() const override;

private:
    int studentID;
};

#endif // DERIVED_H
