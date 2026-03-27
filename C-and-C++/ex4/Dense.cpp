#include "Dense.h"

Dense::Dense (const Matrix &weights, const Matrix &bias, activation_func act)
noexcept (false)
{
  if (bias.get_cols () != 1)
  {
    throw std::domain_error ("ERROR: bias must be with 1 column!");
  }
  if (weights.get_rows () != bias.get_rows ())
  {
    throw std::domain_error ("ERROR: weights and bias must have same amount "
                             "of rows!");
  }
  weights_ = Matrix (weights);
  bias_ = Matrix (bias);
  act_ = act;
}

const Matrix &Dense::get_weights () const noexcept
{
  return weights_;
}

const Matrix &Dense::get_bias () const noexcept
{
  return bias_;
}

activation_func Dense::get_activation () const noexcept
{
  return act_;
}

Matrix Dense::operator() (const Matrix &input) const noexcept (false)
{
  return (*act_) ((weights_ * input) + bias_);
}