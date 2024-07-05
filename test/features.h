// features.h
#ifndef FEATURES_H
#define FEATURES_H

#include <string>
#include <cmath>

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

int add(int a, int b);
void print_message(const char* message);
double multiply(double x, double y);

#endif // FEATURES_H
