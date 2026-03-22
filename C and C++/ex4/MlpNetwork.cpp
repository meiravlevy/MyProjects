#include "MlpNetwork.h"

MlpNetwork::MlpNetwork (const Matrix weights[MLP_SIZE],const Matrix
biases[MLP_SIZE])
noexcept (false): layers_{Dense (weights[0], biases[0], activation::relu),
                          Dense (weights[1], biases[1], activation::relu),
                          Dense (weights[2], biases[2], activation::relu),
                          Dense (weights[3], biases[3], activation::softmax)}
{
  for(int i=0; i<MLP_SIZE - 1;++i)
  {
    if(layers_[i].get_bias().get_rows() != layers_[i+1].get_weights().get_cols())
    {
      throw std::domain_error ("ERROR: wrong dimensions");
    }
  }
}

digit MlpNetwork::operator() (const Matrix &input) const noexcept (false)
{
  Matrix output (input);
  output.vectorize ();
  for (int i = 0; i < MLP_SIZE; ++i)
  {
    output = layers_[i] (output);
  }
  int max_index = output.argmax();
  float prob = output[max_index];
  digit d = {(unsigned int)max_index, prob};
  return d;
}



