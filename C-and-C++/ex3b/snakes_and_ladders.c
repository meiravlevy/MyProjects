#include <string.h> // For strlen(), strcmp(), strcpy()
#include "markov_chain.h"

#define MAX(X, Y) (((X) < (Y)) ? (Y) : (X))

#define EMPTY -1
#define BOARD_SIZE 100
#define MAX_GENERATION_LENGTH 60

#define DICE_MAX 6
#define NUM_OF_TRANSITIONS 20

#define NUM_OF_ARGS 3
#define NO_LADDER_OR_SNAKE (-1)
#define MAX_PATH_LENGTH 60

static MarkovChain *new_markov_chain (void);
static LinkedList *new_linked_list (void);
static void print_cell (void *cell);
static int comp_cell_num (void *cell1, void *cell2);
static void free_cell (void *cell);
static void *copy_cell (const void *src);
static bool is_last_cell (void *cell);
static void add_functions_to_chain (MarkovChain *markov_chain);

/**
 * represents the transitions by ladders and snakes in the game
 * each tuple (x,y) represents a ladder from x to if x<y or a snake otherwise
 */
const int transitions[][2] = {{13, 4},
                              {85, 17},
                              {95, 67},
                              {97, 58},
                              {66, 89},
                              {87, 31},
                              {57, 83},
                              {91, 25},
                              {28, 50},
                              {35, 11},
                              {8,  30},
                              {41, 62},
                              {81, 43},
                              {69, 32},
                              {20, 39},
                              {33, 70},
                              {79, 99},
                              {23, 76},
                              {15, 47},
                              {61, 14}};

/**
 * struct represents a Cell in the game board
 */
typedef struct Cell {
    int number; // Cell number 1-100
    int ladder_to;  // ladder_to represents the jump of the ladder in case
    // there is one from this square
    int snake_to;  // snake_to represents the jump of the snake in case
    // there is one from this square
    //both ladder_to and snake_to should be -1 if the Cell doesn't have them
} Cell;

/** Error handler **/
static int handle_error (char *error_msg, MarkovChain **database)
{
  printf ("%s", error_msg);
  if (database != NULL)
  {
    free_markov_chain (database);
  }
  return EXIT_FAILURE;
}

static int create_board (Cell *cells[BOARD_SIZE])
{
  for (int i = 0; i < BOARD_SIZE; i++)
  {
    cells[i] = malloc (sizeof (Cell));
    if (cells[i] == NULL)
    {
      for (int j = 0; j < i; j++)
      {
        free (cells[j]);
      }
      handle_error (ALLOCATION_ERROR_MASSAGE, NULL);
      return EXIT_FAILURE;
    }
    *(cells[i]) = (Cell) {i + 1, EMPTY, EMPTY};
  }

  for (int i = 0; i < NUM_OF_TRANSITIONS; i++)
  {
    int from = transitions[i][0];
    int to = transitions[i][1];
    if (from < to)
    {
      cells[from - 1]->ladder_to = to;
    }
    else
    {
      cells[from - 1]->snake_to = to;
    }
  }
  return EXIT_SUCCESS;
}

/**
 * fills database
 * @param markov_chain
 * @return EXIT_SUCCESS or EXIT_FAILURE
 */
static int fill_database (MarkovChain *markov_chain)
{
  Cell *cells[BOARD_SIZE];
  if (create_board (cells) == EXIT_FAILURE)
  {
    return EXIT_FAILURE;
  }
  MarkovNode *from_node = NULL, *to_node = NULL;
  size_t index_to;
  for (size_t i = 0; i < BOARD_SIZE; i++)
  {
    add_to_database (markov_chain, cells[i]);
  }

  for (size_t i = 0; i < BOARD_SIZE; i++)
  {
    from_node = get_node_from_database (markov_chain, cells[i])->data;

    if (cells[i]->snake_to != EMPTY || cells[i]->ladder_to != EMPTY)
    {
      index_to = MAX(cells[i]->snake_to, cells[i]->ladder_to) - 1;
      to_node = get_node_from_database (markov_chain, cells[index_to])
          ->data;
      add_node_to_counter_list (from_node, to_node, markov_chain);
    }
    else
    {
      for (int j = 1; j <= DICE_MAX; j++)
      {
        index_to = ((Cell *) (from_node->data))->number + j - 1;
        if (index_to >= BOARD_SIZE)
        {
          break;
        }
        to_node = get_node_from_database (markov_chain, cells[index_to])
            ->data;
        add_node_to_counter_list (from_node, to_node, markov_chain);
      }
    }
  }
  // free temp arr
  for (size_t i = 0; i < BOARD_SIZE; i++)
  {
    free (cells[i]);
  }
  return EXIT_SUCCESS;
}

static MarkovChain *new_markov_chain (void)
{
  return calloc (1, sizeof (MarkovChain));
}

static LinkedList *new_linked_list (void)
{

  return calloc (1, sizeof (LinkedList));
}

static void print_cell (void *cell)
{
  Cell *c = (Cell *) cell;
  printf ("[%d]", c->number);
  if (c->ladder_to != NO_LADDER_OR_SNAKE)
  {
    printf ("-ladder to %d", c->ladder_to);
  }
  else if (c->snake_to != NO_LADDER_OR_SNAKE)
  {
    printf ("-snake to %d", c->snake_to);
  }
  if (c->number != BOARD_SIZE)
  {
    printf (" -> ");
  }
}

static int comp_cell_num (void *cell1, void *cell2)
{
  int *c1 = (int *) cell1;
  int *c2 = (int *) cell2;
  if (*c1 == *c2)
  {
    return 0;
  }
  return 1;
}

static void free_cell (void *cell)
{
  free ((Cell *) cell);
}

static void *copy_cell (const void *src)
{
  struct Cell *dest = malloc (sizeof (struct Cell));
  if (!dest)
  {
    return NULL;
  }
  const char *s = (const char *) src;
  memcpy (dest, s, sizeof (struct Cell));
  return dest;
}

static bool is_last_cell (void *cell)
{
  Cell *c = (Cell *) cell;
  if (c->number == BOARD_SIZE)
  {
    return true;
  }
  return false;
}

static void add_functions_to_chain (MarkovChain *markov_chain)
{
  markov_chain->print_func = print_cell;
  markov_chain->comp_func = comp_cell_num;
  markov_chain->free_data = free_cell;
  markov_chain->copy_func = copy_cell;
  markov_chain->is_last = is_last_cell;
}

/**
 * @param argc num of arguments
 * @param argv 1) Seed
 *             2) Number of sentences to generate
 * @return EXIT_SUCCESS or EXIT_FAILURE
 */
int main (int argc, char *argv[])
{
  if (argc != NUM_OF_ARGS)
  {
    printf ("Usage: seed num_of_of_tweets path words_to_read\n");
    return EXIT_FAILURE;
  }
  unsigned int seed = strtol (argv[1], NULL, 10);
  srand (seed);
  unsigned int num_of_paths = strtol (argv[2], NULL, 10);
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
  add_functions_to_chain (markov_chain); ///must do!
  fill_database (markov_chain);
  for (unsigned int i = 1; i <= num_of_paths; ++i)
  {
    printf ("Random Walk %d: ", i);
    generate_random_sequence (markov_chain,
                              markov_chain->database->first->data,
                              MAX_PATH_LENGTH);
    printf ("\n");
  }
  free_markov_chain (&markov_chain);
  return EXIT_SUCCESS;
}
