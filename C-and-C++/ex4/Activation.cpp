#include "Activation.h"
Matrix activation::relu(const Matrix& m) noexcept(false)
{
  int rows = m.get_rows();
  int cols = m.get_cols();
  Matrix relu_mat(rows, cols);
  for(int i=0; i<rows*cols;++i)
  {
    if(m[i]>=0)
    {
      relu_mat[i] = m[i];
    }
  }
  return relu_mat;
}

Matrix activation::softmax (const Matrix &m) noexcept(false)
{
  int rows = m.get_rows();
  int cols = m.get_cols();
  Matrix exp_m(rows, cols);
  for(int i=0;i<rows*cols;++i)
  {
    exp_m[i] = std::exp (m[i]);
  }
  float exp_m_sum = exp_m.sum();
  return (1/exp_m_sum)*exp_m;
}