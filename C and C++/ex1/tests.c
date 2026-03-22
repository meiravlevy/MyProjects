#include "tests.h"

#include <string.h>

#define K_1 3
#define K_2 2
#define K_3 (-1)
#define K_4 (-3)
#define K_5 29

// See full documentation in header file
int test_encode_non_cyclic_lower_case_positive_k ()
{
  char in[] = "abc";
  char out[] = "def";
  encode (in, K_1);
  return strcmp (in, out) != 0;
}

// See full documentation in header file
int test_encode_cyclic_lower_case_special_char_positive_k ()
{
  // your code goes here
  char in[] = "ba{y";
  char out[] = "dc{a";
  encode (in, K_2);
  return strcmp (in, out) != 0;

}

// See full documentation in header file
int test_encode_non_cyclic_lower_case_special_char_negative_k ()
{
  // your code goes here
  char in[] = "db{h";
  char out[] = "ca{g";
  encode (in, K_3);
  return strcmp (in, out) != 0;

}

// See full documentation in header file
int test_encode_cyclic_lower_case_negative_k ()
{
  // your code goes here
  char in[] = "bch";
  char out[] = "yze";
  encode (in, K_4);
  return strcmp (in, out) != 0;
}

// See full documentation in header file
int test_encode_cyclic_upper_case_positive_k ()
{
  // your code goes here
  char in[] = "XYZ";
  char out[] = "ABC";
  encode (in, K_5);
  return strcmp (in, out) != 0;
}

// See full documentation in header file
int test_decode_non_cyclic_lower_case_positive_k ()
{
  char in[] = "def";
  char out[] = "abc";
  decode (in, K_1);
  return strcmp (in, out) != 0;
}

// See full documentation in header file
int test_decode_cyclic_lower_case_special_char_positive_k ()
{
  // your code goes here
  char in[] = "`a`b_c";
  char out[] = "`y`z_a";
  decode (in, K_2);
  return strcmp (in, out) != 0;
}

// See full documentation in header file
int test_decode_non_cyclic_lower_case_special_char_negative_k ()
{
  // your code goes here
  char in[] = "a`b{c/";
  char out[] = "b`c{d/";
  decode (in, K_3);
  return strcmp (in, out) != 0;
}

// See full documentation in header file
int test_decode_cyclic_lower_case_negative_k ()
{
  // your code goes here
  char in[] = "xyw";
  char out[] = "abz";
  decode (in, K_4);
  return strcmp (in, out) != 0;
}

// See full documentation in header file
int test_decode_cyclic_upper_case_positive_k ()
{
  // your code goes here
  char in[] = "DEF";
  char out[] = "ABC";
  decode (in, K_5);
  return strcmp (in, out) != 0;
}