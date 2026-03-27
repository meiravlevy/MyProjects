//MlpNetwork.h

#ifndef MLPNETWORK_H
#define MLPNETWORK_H

#include "Dense.h"

#define MLP_SIZE 4

/**
 * @struct digit
 * @brief Identified (by Mlp network) digit with
 *        the associated probability.
 * @var value - Identified digit value
 * @var probability - identification probability
 */
typedef struct digit {
    unsigned int value;
    float probability;
} digit;

const Matrix::dims img_dims = {28, 28};
const Matrix::dims weights_dims[] = {{128, 784},
                                     {64,  128},
                                     {20,  64},
                                     {10,  20}};
const Matrix::dims bias_dims[] = {{128, 1},
                                  {64,  1},
                                  {20,  1},
                                  {10,  1}};

// Insert MlpNetwork class here...
class MlpNetwork {
 public:
  MlpNetwork (const Matrix weights[MLP_SIZE],const Matrix biases[MLP_SIZE])
  noexcept (false);
  digit operator() (const Matrix &input) const noexcept (false);
 private:
  Dense layers_[MLP_SIZE];
};
#endif // MLPNETWORK_H
