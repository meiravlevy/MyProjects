#include "markov_chain.h"
#define MAX_LINE 1000
#define MAX_ARGS 5
#define MIN_ARGS 4
#define MAX_TWEET_LENGTH 20
static MarkovChain *new_markov_chain (void);
static LinkedList *new_linked_list (void);
static void print_string (void *str);
static int my_strcmp (void *a, void *b);
static bool is_word_last (void *data);
static void free_string (void *to_free);
static void *copy_string (const void *src);
static void add_functions_to_chain (MarkovChain *markov_chain);

static void print_string (void *str)
{
  char *s = (char *)str;
  size_t len_s = strlen (s);
  printf ("%s", (char *) str);
  if (s[len_s - 1] != '.')
  {
    printf(" ");
  }
}

static int my_strcmp (void *a, void *b)
{
  return (strcmp ((const char *) a, (const char *) b));
}

static void free_string (void *to_free)
{
  free ((char *) to_free);
}

static void *copy_string (const void *src)
{
  const char *s = (const char *) src;
  char *dest = malloc (strlen (s) + 1);
  if (!dest)
  {
    return NULL;
  }
  strcpy (dest, s);
  return dest;
}

static bool is_word_last (void *data)
{
  char *word = (char *) data;
  size_t len_word = strlen (word);
  if (word[len_word - 1] != '.')
  {
    return false;
  }
  return true;
}

static MarkovChain *new_markov_chain (void)
{
  return calloc (1, sizeof (MarkovChain));
}

static LinkedList *new_linked_list (void)
{
  return calloc (1, sizeof (LinkedList));
}


static int fill_database (FILE *fp, int words_to_read, MarkovChain
*markov_chain)
{
  int counter = 0;
  char buffer[MAX_LINE + 1];
  while (fgets (buffer, MAX_LINE + 1, fp))
  {
    char *token = strtok (buffer, " \r\n");
    Node *tmp = NULL;
    Node *last_node = NULL;
    while (((words_to_read == 0) || counter < words_to_read) && token)
    {
      last_node = add_to_database (markov_chain, token);
      if (!last_node)
      {
        printf (ALLOCATION_ERROR_MASSAGE);
        return EXIT_FAILURE;
      }
      if (tmp)
      {
        if (!(markov_chain->is_last(tmp->data->data)) &&
        (!add_node_to_counter_list
        (tmp->data,last_node->data, markov_chain)))
        {
          printf (ALLOCATION_ERROR_MASSAGE);
          return EXIT_FAILURE;
        }
      }
      counter++;
      tmp = last_node;
      token = strtok (NULL, " \r\n");
    }
  }
  return EXIT_SUCCESS;
}

static void add_functions_to_chain (MarkovChain *markov_chain)
{
  markov_chain->print_func = print_string;
  markov_chain->comp_func = my_strcmp;
  markov_chain->free_data = free_string;
  markov_chain->copy_func = copy_string;
  markov_chain->is_last = is_word_last;
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
  add_functions_to_chain (markov_chain);
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