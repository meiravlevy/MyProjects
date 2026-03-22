#include "Matrix.h"

Matrix::Matrix (int rows, int cols) noexcept (false)
{
  if (rows <= 0 or cols <= 0)
  {
    throw std::domain_error ("ERROR: rows and cols must be positive!");
  }
  this->rows_ = rows;
  this->cols_ = cols;
  this->mat_ = new float[rows_ * cols_]{};
}

Matrix::Matrix (const Matrix &m) noexcept (false): Matrix (m.rows_, m.cols_)
{
  for (int i = 0; i < rows_; ++i)
  {
    for (int j = 0; j < cols_; ++j)
    {
      mat_[i * cols_ + j] = m.mat_[i * m.cols_ + j];
    }
  }
}

Matrix &Matrix::transpose () noexcept
{
  const Matrix temp (*this); //calls copy constructor
  this->rows_ = temp.cols_;
  this->cols_ = temp.rows_;
  for (int i = 0; i < rows_; ++i)
  {
    for (int j = 0; j < cols_; ++j)
    {
      this->mat_[i * this->cols_ + j] = temp.mat_[j * temp.cols_ + i];
    }
  }
  return *this;
}

Matrix &Matrix::vectorize () noexcept
{
  rows_ = rows_ * cols_;
  cols_ = 1;
  return *this;
}

void Matrix::plain_print () const noexcept
{
  for (int i = 0; i < rows_; ++i)
  {
    for (int j = 0; j < cols_; ++j)
    {
      std::cout << mat_[i * cols_ + j] << " ";
    }
    std::cout << std::endl;
  }
}

Matrix Matrix::dot (const Matrix &other) const noexcept (false)
{
  if ((rows_ != other.rows_) or (cols_ != other.cols_))
  {
    throw std::domain_error ("ERROR: matrix sent must have same dimensions!");
  }
  Matrix new_m (rows_, cols_);
  for (int i = 0; i < rows_ * cols_; ++i)
  {
    new_m.mat_[i] = mat_[i] * other.mat_[i];
  }
  return new_m;
}
float Matrix::sum () const noexcept
{
  float sum = 0;
  for (int i = 0; i < rows_ * cols_; ++i)
  {
    sum += mat_[i];
  }
  return sum;
}
float Matrix::norm () const noexcept
{
  float sum_of_squares = 0;
  for (int i = 0; i < rows_ * cols_; ++i)
  {
    sum_of_squares += mat_[i] * mat_[i];
  }
  return std::sqrt (sum_of_squares);
}

int Matrix::argmax () const noexcept
{
  float max_m_elem = mat_[0];
  int max_ind = 0;
  for (int i = 1; i < rows_ * cols_; ++i)
  {
    if (mat_[i] > max_m_elem)
    {
      max_m_elem = mat_[i];
      max_ind = i;
    }
  }
  return max_ind;
}

Matrix &Matrix::operator+= (const Matrix &rhs) noexcept (false)
{
  if ((rows_ != rhs.rows_) or (cols_ != rhs.cols_))
  {
    throw std::domain_error ("ERROR: rhs matrix must have same dimensions!");
  }
  for (int i = 0; i < rows_ * cols_; ++i)
  {
    mat_[i] += rhs.mat_[i];
  }
  return *this;
}

Matrix Matrix::operator+ (const Matrix &rhs) const noexcept (false)
{
  if ((rows_ != rhs.rows_) or (cols_ != rhs.cols_))
  {
    throw std::domain_error ("ERROR: rhs matrix must have same dimensions!");
  }
  Matrix addition_mat (rows_, cols_);
  for (int i = 0; i < rows_ * cols_; ++i)
  {
    addition_mat.mat_[i] = mat_[i] + rhs.mat_[i];
  }
  return addition_mat;
}

Matrix &Matrix::operator= (const Matrix &rhs) noexcept (false)
{
  if (&rhs != this)
  {
    delete[] mat_;
    rows_ = rhs.rows_;
    cols_ = rhs.cols_;
    mat_ = new float[rows_ * cols_]{};
    for (int i = 0; i < rows_ * cols_; ++i)
    {
      mat_[i] = rhs.mat_[i];
    }
  }
  return *this;
}

Matrix Matrix::operator* (const Matrix &rhs) const noexcept (false)
{
  if ((cols_ != rhs.rows_))
  {
    throw std::domain_error ("ERROR: to multiply, lhs cols and rhs rows must "
                             "be equal!");
  }
  Matrix mult_m (rows_, rhs.cols_);
  for (int i = 0; i < mult_m.rows_; ++i)
  {
    for (int j = 0; j < mult_m.cols_; ++j)
    {
      float sum_cord = 0;
      //multiplying row i of this matrix and column j of rhs matrix:
      for (int k = 0; k < cols_; k++)
      {
        sum_cord += mat_[i * cols_ + k] * rhs.mat_[k * rhs.cols_ + j];
      }
      mult_m.mat_[i * mult_m.cols_ + j] = sum_cord;
    }
  }
  return mult_m;
}

Matrix Matrix::operator* (float c) const noexcept (false)
{
  return c * (*this);
}

float &Matrix::operator() (int i, int j) noexcept (false)
{
  if (i < 0 or i > (rows_ - 1) or j < 0 or (j > cols_ - 1))
  {
    throw std::out_of_range ("ERROR: index of matrix is out of range!");
  }
  return mat_[i * cols_ + j];
}

const float &Matrix::operator() (int i, int j) const noexcept (false)
{
  if (i < 0 or i > (rows_ - 1) or j < 0 or (j > cols_ - 1))
  {
    throw std::out_of_range ("ERROR: index of matrix is out of range!");
  }
  return mat_[i * cols_ + j];
}

float &Matrix::operator[] (int i) noexcept (false)
{
  if (i < 0 or i > ((rows_ * cols_) - 1))
  {
    throw std::out_of_range ("ERROR: Index of matrix is out of range!");
  }
  return mat_[i];
}

const float &Matrix::operator[] (int i) const noexcept (false)
{
  if (i < 0 or i > ((rows_ * cols_) - 1))
  {
    throw std::out_of_range ("ERROR: Index of matrix is out of range!");
  }
  return mat_[i];
}

Matrix operator* (float c, const Matrix &m) noexcept (false)
{
  Matrix c_m (m.get_rows(), m.get_cols());
  for (int i = 0; i < m.get_rows() * m.get_cols(); ++i)
  {
    c_m[i] = c * m[i];
  }
  return c_m;
}

std::ostream &operator<< (std::ostream &os, const Matrix &m) noexcept
{
  for (int i = 0; i < m.rows_; ++i)
  {
    for (int j = 0; j < m.cols_; ++j)
    {
      (m(i,j)> PRINT_CONDITION) ? os<<"**" : os<<"  ";
    }
    os << std::endl;
  }
  return os;
}

std::istream& operator>>(std::istream &is, Matrix &m) noexcept(false)
{
  char* buf = (char *)m.mat_;
  auto buf_size = (std::streamsize)(m.rows_*m.cols_*sizeof(float));
  is.read (buf, buf_size);
  if(!is)
  {
    throw std::runtime_error("ERROR: couldn't read input");
  }
  return is;
}
