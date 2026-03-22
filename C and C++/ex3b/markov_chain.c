#include "markov_chain.h"

/**
* Get random number between 0 and max_number [0, max_number).
* @param max_number maximal number to return (not including)
* @return Random number
*/

int get_random_number (int max_number)
{
  return rand () % max_number;
}

Node *get_i_node_in_linked_list (int i, LinkedList *linked_list)
{
  Node *cur_node = linked_list->first;
  for (int j = 0; j < i; ++j)
  {
    cur_node = cur_node->next;
  }
  return cur_node;
}

MarkovNode *get_first_random_node (MarkovChain *markov_chain)
{
  LinkedList *linked_list = markov_chain->database;
  int i;
  Node *node_i = NULL;
  do
  {
    i = get_random_number (linked_list->size);
    node_i = get_i_node_in_linked_list (i, linked_list);
  }
  while (markov_chain->is_last ((void *) node_i->data->data));
  return node_i->data; //this is the markovNode *
}

size_t sum_freq_in_counter_list (MarkovNode *state_struct_ptr)
{
  NextNodeCounter *counter_list = state_struct_ptr->counter_list;
  size_t sum_freq = 0;
  for (size_t i = 0; i < state_struct_ptr->counter_list_size; i++)
  {
    sum_freq += counter_list[i].frequency;
  }
  return sum_freq;
}

MarkovNode *get_next_random_node (MarkovNode *state_struct_ptr)
{
  int sum_freq = (int) sum_freq_in_counter_list (state_struct_ptr);
  int cur_sum_freq = -1;
  int i = get_random_number (sum_freq);
  NextNodeCounter *counter_list = state_struct_ptr->counter_list;
  size_t j = 0;
  for (; j < state_struct_ptr->counter_list_size; ++j)
  {
    cur_sum_freq += (int) counter_list[j].frequency;
    if (cur_sum_freq >= i)
    {
      break;
    }
  }
  return counter_list[j].markov_node;
}

void generate_random_sequence (MarkovChain *markov_chain, MarkovNode *
first_node, int max_length)
{
  MarkovNode *cur_m_node = first_node;
  if (!cur_m_node)
  {
    cur_m_node = get_first_random_node (markov_chain);
  }
  for (int word_counter = 0; word_counter < max_length; ++word_counter)
  {
    markov_chain->print_func (cur_m_node->data);
    if (markov_chain->is_last (cur_m_node->data) || word_counter ==
                                                    (max_length - 1))
    {
      break;
    }
    cur_m_node = get_next_random_node (cur_m_node);
  }
}

void free_node (Node *node, MarkovChain *markov_chain)
{
  markov_chain->free_data (node->data->data);
  node->data->data = NULL;
  if(node->data->counter_list)
  {
    free (node->data->counter_list);
    node->data->counter_list = NULL;
  }
  free (node->data);
  node->data = NULL;
  free (node);
}

void free_markov_chain (MarkovChain **ptr_chain)
{
  if (ptr_chain)
  {
    Node *cur_node = (*ptr_chain)->database->first, *next = NULL;
    while (cur_node)
    {
      next = cur_node->next;
      free_node (cur_node, *ptr_chain);
      cur_node = next;
    }
    free ((*ptr_chain)->database);
    (*ptr_chain)->database = NULL;
    free (*ptr_chain);
    *ptr_chain = NULL;
  }
}

int
is_markov_node_in_counter_list (MarkovNode *first_node, MarkovNode
*second_node, MarkovChain *markov_chain)
{
  for (size_t i = 0; i < first_node->counter_list_size; ++i)
  {
    if (!(markov_chain->comp_func (first_node->counter_list[i]
                                       .markov_node->data, second_node->data)))
    {
      return (int) i;
    }
  }
  return -1;
}

bool add_node_to_counter_list (MarkovNode *first_node, MarkovNode
*second_node, MarkovChain *markov_chain)
{
  if (!(first_node->counter_list))
  {
    NextNodeCounter *new_counter_list = (NextNodeCounter *) malloc
        (sizeof (NextNodeCounter));
    if (!new_counter_list)
    {
      return false;
    }
    first_node->counter_list = new_counter_list;
    first_node->counter_list_size = 1;
  }
  else
  {
    int i = is_markov_node_in_counter_list (first_node, second_node,
                                            markov_chain);
    if (i >= 0)
    {
      first_node->counter_list[i].frequency++;
      return true;
    }
    NextNodeCounter *tmp = realloc (first_node->counter_list,
                                    sizeof (NextNodeCounter)
                                    * (first_node->counter_list_size + 1));
    if (!tmp)
    {
      return false;
    }
    first_node->counter_list = tmp;
    first_node->counter_list_size++;
  }
  //conversion from MarkovNode to NextNodeCounter so it can go into
  // counter_list:
  NextNodeCounter second = {second_node, 1};
  first_node->counter_list[first_node->counter_list_size - 1] = second;
  return true;
}

Node *get_node_from_database (MarkovChain *markov_chain, void *data_ptr)
{
  LinkedList *database = markov_chain->database;
  Node *cur_node = database->first;
  for (int i = 0; i < database->size; ++i)
  {
    if (!(markov_chain->comp_func ((void *) cur_node->data->data, data_ptr)))
    {
      return cur_node;
    }
    cur_node = cur_node->next;
  }
  return NULL;
}

Node *add_to_database (MarkovChain *markov_chain, void *data_ptr)
{
  if (markov_chain->database)
  {
    Node *is_node = get_node_from_database (markov_chain, data_ptr);
    if (is_node)
    {
      return is_node;
    }
  }
  MarkovNode *new_m_node = malloc (sizeof (MarkovNode));
  if (!new_m_node)
  {
    return NULL;
  }
  if (!(new_m_node->data = markov_chain->copy_func (data_ptr)))
  {
    free(new_m_node);
    new_m_node = NULL;
    return NULL;
  }
  new_m_node->counter_list = NULL;
  new_m_node->counter_list_size = 0;
  if (add (markov_chain->database, (void *) new_m_node))
  {
    markov_chain->free_data(new_m_node->data);
    new_m_node->data = NULL;
    free (new_m_node);
    new_m_node = NULL;
    return NULL;
  }
  return markov_chain->database->last;
}