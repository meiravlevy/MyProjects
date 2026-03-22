#include "cipher.h"
#include "tests.h"


// your code goes here
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

#define TEST "test"
#define ENCODE "encode"
#define DECODE "decode"
#define ONE_ARG 2
#define FOUR_ARG 5
#define MAX_LINE 1025

int is_integer (char const *str, size_t str_length);
int encode_or_decode_file (char *argv[]);
void do_command (char command[], int k, FILE *in_f, FILE *out_f);
int do_tests ();

int is_integer (char const *str, size_t str_length)
{
  for (size_t i = 0; i < str_length; i++)
  {
    //if first character is minus and there is a digit:
    if ((i == 0) && (str_length > 1) && (str[0] == '-'))
    {
      continue;
    }
    else if (isdigit(str[i]) == false)
    {
      return false;
    }
  }
  return true;
}

int do_tests ()
{
  if (test_encode_non_cyclic_lower_case_positive_k () != 0
      || test_encode_cyclic_lower_case_special_char_positive_k () != 0
      || test_encode_non_cyclic_lower_case_special_char_negative_k () != 0
      || test_encode_cyclic_lower_case_negative_k () != 0
      || test_encode_cyclic_upper_case_positive_k () != 0
      || test_decode_non_cyclic_lower_case_positive_k () != 0
      || test_decode_cyclic_lower_case_special_char_positive_k () != 0
      || test_decode_non_cyclic_lower_case_special_char_negative_k () != 0
      || test_decode_cyclic_lower_case_negative_k () != 0
      || test_decode_cyclic_upper_case_positive_k () != 0)
  {
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}

//encodes or decodes into output file:
void do_command (char command[], int k, FILE *in_f, FILE *out_f)
{
  if (strcmp (command, ENCODE) == 0)
  {
    char line[MAX_LINE] = {0};
    while (fgets (line, MAX_LINE, in_f))
    {
      encode (line, (int) k);
      fputs (line, out_f);
    }
  }
  else
  {
    char line[MAX_LINE] = {0};
    while (fgets (line, MAX_LINE, in_f))
    {
      decode (line, (int) k);
      fputs (line, out_f);
    }
  }
  fclose (in_f);
  fclose (out_f);
}

//checks if path to files are valid and if so, encodes or decodes them:
int encode_or_decode_file (char *argv[])
{
  FILE *in_f = fopen (argv[3], "r");
  if (in_f == NULL) //if input file is invalid
  {
    fprintf (stderr, "The given file is invalid.\n");
    return EXIT_FAILURE;
  }
  else
  {
    FILE *out_f = fopen (argv[4], "w");
    if (out_f == NULL) //if output file is invalid
    {
      fclose (in_f);
      fprintf (stderr, "The given file is invalid.\n");
      return EXIT_FAILURE;
    }
    int k = (int) strtol (argv[2], NULL, 10);
    do_command (argv[1], k, in_f, out_f);
  }
  return EXIT_SUCCESS;
}

int main (int argc, char *argv[])
{
  if ((argc != ONE_ARG) && (argc != FOUR_ARG))
  {
    fprintf (stderr, "The program receives 1 or 4 arguments only.\n");
    return EXIT_FAILURE;
  }
  else if (argc == 2)
  {
    if (strcmp (argv[1], TEST) != 0) //checks if the given arg is "test"
    {
      fprintf (stderr, "Usage: cipher test\n");
      return EXIT_FAILURE;
    }
    return do_tests ();
  }
  else //when we have 5 arguments
  {
    //checks if the command is "encode" or "decode":
    if ((strcmp (argv[1], ENCODE) != 0) && (strcmp (argv[1], DECODE) != 0))
    {
      fprintf (stderr, "The given command is invalid.\n");
      return EXIT_FAILURE;
    }
      //checks if k is valid:
    else if (is_integer (argv[2], strlen (argv[2])) == false)
    {
      fprintf (stderr, "The given shift value is invalid.\n");
      return EXIT_FAILURE;
    }
    else
    {
      return encode_or_decode_file (argv);
    }
  }
}