#include "cipher.h"

/// IN THIS FILE, IMPLEMENT EVERY FUNCTION THAT'S DECLARED IN cipher.h.


#include <ctype.h>
#define NUM_OF_ALPHA 26


// See full documentation in header file

void right_k_indent (char s[], int i, int k)
{
  char min;
  char max;
  if (islower(s[i])) ///check how to turn into one function
  {
    min = 'a';
    max = 'z';
  }
  else
  {
    min = 'A';
    max = 'Z';
  }

  if ((s[i] + k) > max) //if the char after indentation is not lower
  {
    //the indentation needed from a after we pass the letter z:
    int remainder = (k - (max - s[i]) - 1);
    s[i] = (char) (min + remainder);
  }
  else
  {
    s[i] = (char) (s[i] + k);
  }

}

void left_k_indent (char s[], int i, int k)
{
  char min;
  char max;
  if (islower(s[i])) //make this a macro and do it in negative as well
  {
    min = 'a';
    max = 'z';
  }
  else
  {
    min = 'A';
    max = 'Z';
  }
  if ((s[i] + k) < min) //if the char after indentation is not lower
  {
    //the indentation needed from a after we pass the letter z:
    int remainder = (k - (min - s[i]) + 1);
    s[i] = (char) (max + remainder);
  }
  else
  {
    s[i] = (char) (s[i] + k);
  }
}

void encode (char s[], int k)
{
  k = k % NUM_OF_ALPHA;
  int i = 0;
  while (s[i] != '\0')
  {
    if (isalpha(s[i]))
    {
      if (k >= 0)
      {
        right_k_indent (s, i, k);
      }
      else
      {
        left_k_indent (s, i, k);
      }
    }
    i++;
  }
}

// See full documentation in header file
void decode (char s[], int k)
{
  k = k % NUM_OF_ALPHA;
  int i = 0;
  while (s[i] != '\0')
  {
    if (isalpha(s[i]))
    {
      if (k >= 0)
      {
        left_k_indent (s, i, -k);
      }
      else
      {
        right_k_indent (s, i, -k);
      }
    }
    i++;
  }
}



