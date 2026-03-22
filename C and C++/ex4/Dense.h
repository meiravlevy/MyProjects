#ifndef DENSE_H
#define DENSE_H

#include "Activation.h"

// Insert Dense class here...
class Dense {
 public:
  Dense (const Matrix &weights, const Matrix &bias, activation_func act)
  noexcept (false);
  const Matrix &get_weights () const noexcept;
  const Matrix &get_bias () const noexcept;
  activation_func get_activation () const noexcept;
  Matrix operator() (const Matrix &input) const noexcept (false);
 private:
  Matrix weights_;
  Matrix bias_;
  activation_func act_;
};

#endif //DENSE_H
