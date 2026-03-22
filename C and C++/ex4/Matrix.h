#ifndef MATRIX_H
#define MATRIX_H
#include <exception>
#include <iostream>
#include <cmath>
#define PRINT_CONDITION 0.1
class Matrix {

 public:
  /**
   * @struct dims
   * @brief Matrix dimensions container. Used in MlpNetwork.h and main.cpp
   */
  struct dims {
      int rows, cols;
  };
  Matrix (int rows, int cols) noexcept (false);
  Matrix () noexcept (false): Matrix (1, 1)
  {};
  Matrix (const Matrix &m) noexcept (false);
  ~Matrix ()
  { delete[] mat_; };
  const int &get_rows () const noexcept
  { return rows_; };
  const int &get_cols () const noexcept
  { return cols_; };
  Matrix &transpose () noexcept;
  Matrix &vectorize () noexcept;
  void plain_print () const noexcept;
  Matrix dot (const Matrix &other) const noexcept (false);
  float sum () const noexcept;
  float norm () const noexcept;
  int argmax () const noexcept;
  Matrix &operator+= (const Matrix &rhs) noexcept (false);
  Matrix operator+ (const Matrix &rhs) const noexcept (false);
  Matrix &operator= (const Matrix &rhs) noexcept (false);
  Matrix operator* (const Matrix &rhs) const noexcept (false);
  Matrix operator* (float c) const noexcept (false);
  float &operator()(int i, int j) noexcept(false);
  const float &operator() (int i, int j) const noexcept (false);
  float &operator[] (int i) noexcept (false);
  const float &operator[] (int i) const noexcept (false);
  friend Matrix operator* (float c, const Matrix &m) noexcept (false);
  friend std::ostream& operator<<(std::ostream &os, const Matrix &m) noexcept;
  friend std::istream& operator>>(std::istream &is, Matrix &m)
  noexcept(false);
 private:
  int rows_;
  int cols_;
  float *mat_;
};

#endif //MATRIX_H
