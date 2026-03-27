#include "markov_chain.h"
#define MAX_LINE 1000
#define MAX_ARGS 5
#define MIN_ARGS 4
#define MAX_TWEET_LENGTH 20

MarkovChain *new_markov_chain (void)
{
  return calloc (1, sizeof (MarkovChain));
}

LinkedList *new_linked_list (void)
{

  return calloc (1, sizeof (LinkedList));
}

bool read_and_add_words_from_line (int words_to_read, int *counter, char
*buffer, MarkovChain *markov_chain)
{
  char *token = strtok (buffer, " \r\n");
  Node *tmp = NULL;
  Node *last_node = NULL;
  while (((!words_to_read) || *counter < words_to_read) && token)
  {
    last_node = add_to_database (markov_chain, token);
    if (!last_node)
    {
      return false;
    }
    if (tmp)
    {
      if (!add_node_to_counter_list (tmp->data, last_node->data))
      {
        return false;
      }
    }
    (*counter)++;
    tmp = last_node;
    token = strtok (NULL, " \r\n");
  }
  return true;
}

int fill_database (FILE *fp, int words_to_read, MarkovChain *markov_chain)
{
  int counter = 0;
  char buffer[MAX_LINE + 1];
  while (fgets (buffer, MAX_LINE + 1, fp))
  {
    if (!(read_and_add_words_from_line (words_to_read, &counter, buffer,
                                        markov_chain)))
    {
      printf (ALLOCATION_ERROR_MASSAGE);
      return EXIT_FAILURE;
    }
  }

  return EXIT_SUCCESS;
}

int main (int argc, char *argv[])
{
  if (argc > MAX_ARGS || argc < MIN_ARGS)
  {
    printf ("Usage: seed num_of_of_tweets path words_to_read\n");
    return EXIT_FAILURE;
  }
  unsigned int seed = strtol (argv[1], NULL, 10);
  srand (seed);
  unsigned int num_of_tweets = strtol (argv[2], NULL, 10);
  FILE *fp = fopen (argv[3], "r");
  if (!fp)
  {
    printf ("Error: the given file is invalid.\n");
    return EXIT_FAILURE;
  }
  unsigned int words_to_read;
  if (argc == MAX_ARGS)
  {
    words_to_read = strtol (argv[4], NULL, 10);
  }
  else
  {
    words_to_read = 0;
  }
  MarkovChain *markov_chain = new_markov_chain ();
  if (!markov_chain)
  {
    printf (ALLOCATION_ERROR_MASSAGE);
    return EXIT_FAILURE;
  }
  LinkedList *linked_list = new_linked_list ();
  if (!linked_list)
  {
    printf (ALLOCATION_ERROR_MASSAGE);
    return EXIT_FAILURE;
  }
  markov_chain->database = linked_list;
  fill_database (fp, (int) words_to_read, markov_chain);
  for (unsigned int i = 1; i <= num_of_tweets; ++i)
  {
    printf ("Tweet %d: ", i);
    generate_random_sequence (markov_chain, NULL,
                              MAX_TWEET_LENGTH);
    printf ("\n");
  }
  free_markov_chain (&markov_chain);
  fclose (fp);

  return EXIT_SUCCESS;
}