// tests/test_class.h

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
