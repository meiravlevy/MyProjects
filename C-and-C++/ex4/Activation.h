#include "Matrix.h"

#ifndef ACTIVATION_H
#define ACTIVATION_H

// Insert activation namespace here...
typedef Matrix(*activation_func)(const Matrix& m);
namespace activation
{
    Matrix relu(const Matrix& m) noexcept(false);
    Matrix softmax(const Matrix& m) noexcept(false);
}

#endif //ACTIVATION_H