class FriendClass {
public:
    FriendClass() {}

    void friendMethod(TestClass& obj) {
        obj.privateMember = 10.0;  // Access private member of TestClass
    }
};
