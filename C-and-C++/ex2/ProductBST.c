#include "ProductBST.h"
#include <string.h>
#include <ctype.h>

#define MAX_LINE 1025
#define SUCCESS 0
#define NEGATIVE_NUMBER (-1)
#define FAILURE_INVALID_LINE 2

char *allocate_and_cpy (char *src);
Node *new_node (char *name, int quantity);
Node *add_new_node_to_bst (Node **cur_node, char *name, int quantity);
int is_str_number (const char *tok);
Node *get_father_by_child_name (Node *root, char *name);
Node *get_existing_child_from_father (Node *node_father, char *name);
void delete_leaf (Node **root, Node **p2father, Node *node_of_product);
void delete_node_with_one_child (Node **p2root, Node **p2father,
                                 Node *node_of_product);
Node *find_successor (Node *node_of_product);



char *allocate_and_cpy (char *src)
{
  char *dest = malloc (strlen (src) + 1);
  if (!dest)
  {
    return NULL;
  }
  strcpy (dest, src);
  return dest;
}

Node *new_node (char *name, int quantity) //create a new node with model
{
  Node *new_model = malloc (sizeof (Node));
  if (!new_model)
  {
    fprintf (stderr, "%s%s", ERROR, ALLOCATION_FAILED);
    return NULL;
  }
  if (!(new_model->product.name = allocate_and_cpy (name)))
  {
    free (new_model);
    new_model = NULL;
    fprintf (stderr, "%s%s", ERROR, ALLOCATION_FAILED);
  }
  else
  {
    new_model->product.quantity = quantity;
    new_model->right_child = NULL;
    new_model->left_child = NULL;
  }
  return new_model;
}

Node *add_new_node_to_bst (Node **cur_node, char *name, int quantity)
{
  if (!(*cur_node)) //if tree is empty do:
  {
    (*cur_node) = new_node (name, quantity);
  }
  else if (!(strcmp (name, (*cur_node)->product.name)))
  {
    fprintf (stderr, "%s%s", ERROR, PRODUCT_EXISTS);
  }
  else if (strcmp (name, (*cur_node)->product.name) > 0)
  {
    return add_new_node_to_bst (&((*cur_node)->right_child), name,
                                quantity);
  }
  else
  {
    return add_new_node_to_bst (&((*cur_node)->left_child), name,
                                quantity);
  }
  return (*cur_node);
}

Node *add_product (Node *root, char *name, int quantity)
{

  if (quantity < 1)
  {
    fprintf (stderr, "%s%s", ERROR, INVALID_QUANTITY);
    return root;
  }
  if (!name)
  {
    fprintf (stderr, "%s%s", ERROR, INVALID_POINTER);
    return root;
  }
  //adds new node to bst and if not successful, is_added will be NULL:
  Node *is_added = add_new_node_to_bst (&root, name, quantity);
  if (!is_added)
  {
    return NULL;
  }
  return root;
}

int is_str_number (const char *tok)
{
  for (int i = 1; tok[i] != '\0'; i++)
  {
    if (tok[i] == '\r')
    {
      continue;
    }
    if ((i == 1) && tok[1] == '-')
    {
      return NEGATIVE_NUMBER;
    }
    else if (!(isdigit(tok[i])))
    {
      return FAILURE_INVALID_LINE;
    }
  }
  return SUCCESS;
}

Node *build_bst (const char *filename)
{
  if (!filename)
  {
    fprintf (stderr, "%s%s", ERROR, INVALID_POINTER);
    return NULL;
  }
  FILE *fp = fopen (filename, "r");
  if (!fp)
  {
    fprintf (stderr, "%s%s", ERROR, FILE_OPEN_FAILED);
    return NULL;
  }
  char line[MAX_LINE] = {0};
  Node *root = NULL;
  while (fgets (line, MAX_LINE, fp))
  {
    char *name = strtok (line, ":");
    char *quant_str = strtok (NULL, "\n");
    if (is_str_number (quant_str) == FAILURE_INVALID_LINE)
    {
      fprintf (stderr, "%s%s", ERROR, INVALID_LINE);
      continue;
    }
    else if (is_str_number (quant_str) == NEGATIVE_NUMBER)
    {
      root = add_product (root, name, NEGATIVE_NUMBER);
      continue;
    }
    else
    {
      int quantity = (int) (strtol (quant_str, NULL, 10));
      root = add_product (root, name, quantity);
      if (!root)
      {
        break;
      }
    }
  }
  fclose (fp);
  return root;
}

Node *get_father_by_child_name (Node *root, char *name)
{
  Node *cur_node = root;
  Node *father = root;
  while (cur_node)
  {
    if (!(strcmp (name, cur_node->product.name)))
    {
      return father;
    }
    else if (strcmp (name, cur_node->product.name) > 0)
    {
      father = cur_node;
      cur_node = cur_node->right_child;
    }
    else
    {
      father = cur_node;
      cur_node = cur_node->left_child;
    }
  }
  return NULL;
}

//son exists. check if product is left or right of the father, or father
// has no children which means root is the node with the name:

Node *get_existing_child_from_father (Node *node_father, char *name)
{
  if (node_father->right_child
      && (!(strcmp (name, node_father->right_child->product.name))))
  {
    return node_father->right_child;

  }
  else if (node_father->left_child
           && (!(strcmp (name, node_father->left_child->product.name))))
  {
    return node_father->left_child;
  }
  return node_father;
}

Product *search_product (Node *root, char *name)
{
  if (!name)
  {
    fprintf (stderr, "%s%s", ERROR, INVALID_POINTER);
    return NULL;
  }
  if (!root)
  {
    return NULL;
  }
  Node *node_father = get_father_by_child_name (root, name);

  if (!node_father)
  {
//    fprintf (stderr, "%s%s", ERROR, PRODUCT_NOT_FOUND);
    return NULL;
  }
  Node *product_node = get_existing_child_from_father (node_father, name);
  return &(product_node->product);
}

void free_node (Node **p2node)
{
  free ((*p2node)->product.name);
  (*p2node)->product.name = NULL;
  free (*p2node);
  *p2node = NULL;
}

void delete_leaf (Node **root, Node **p2father, Node *node_of_product)
{
  if ((*p2father)->right_child == node_of_product) //if node is right child
  {
    (*p2father)->right_child = NULL;
    free_node (&node_of_product);
  }
  else if ((*p2father)->left_child == node_of_product) //if node is left child
  {
    (*p2father)->left_child = NULL;
    free_node (&node_of_product);
  }
  else //deleting the root
  {
    free_node (&node_of_product);
    (*root) = NULL;
    p2father = NULL;
  }
}

void delete_node_with_one_child (Node **p2root, Node **p2father,
                                 Node *node_of_product)
{
  Node *child = NULL;
  //assign child of node to be deleted, so we can link it later to the father:
  if (!(child = node_of_product->right_child))
  {
    child = node_of_product->left_child;
  }
  if (node_of_product == (*p2root)) //if node to be deleted is root
  {
    delete_leaf (p2root, p2father, node_of_product);
    (*p2root) = child;
  }
  else
  {
    //if node to be deleted is a right child:
    if ((*p2father)->right_child == node_of_product)
    {
      delete_leaf (p2root, p2father, node_of_product);
      (*p2father)->right_child = child;
    }
    else //if node to be deleted is left child
    {
      delete_leaf (p2root, p2father, node_of_product);
      (*p2father)->left_child = child;
    }
  }
}

Node *find_successor (Node *node_of_product)
{
  Node *cur_node = node_of_product->right_child;
  while (cur_node->left_child)
  {
    cur_node = cur_node->left_child;
  }
  return cur_node;
}

Node *delete_product (Node *root, char *name)
{
  if (!name)
  {
    fprintf (stderr, "%s%s", ERROR, INVALID_POINTER);
    return root;
  }
  if (!root)
  {
    fprintf (stderr, "%s%s", ERROR, PRODUCT_NOT_FOUND);
    return NULL;
  }
  Node *node_father = get_father_by_child_name (root, name);
  if (!node_father)
  {
    fprintf (stderr, "%s%s", ERROR, PRODUCT_NOT_FOUND);
    return root;
  }
  Node *node_of_product = get_existing_child_from_father (node_father, name);
  if ((!(node_of_product->right_child)) && (!(node_of_product->left_child)))
  {
    delete_leaf (&root, &node_father, node_of_product);
  }
  else if ((node_of_product->right_child && (!node_of_product->left_child))
           || (node_of_product->left_child && (!node_of_product->right_child)))
  {
    delete_node_with_one_child (&root, &node_father,
                                node_of_product);
  }
  else
  {
    Node *successor = find_successor (node_of_product);
    char *new_name = allocate_and_cpy (successor->product.name);
    if (!new_name)
    {
      fprintf (stderr, "%s%s", ERROR, ALLOCATION_FAILED);
      return NULL;
    }
    Node *father_of_successor = get_father_by_child_name (
        root, successor->product.name);
    free (node_of_product->product.name);
    node_of_product->product.name = new_name;
    node_of_product->product.quantity = successor->product.quantity;
    if (successor->right_child)
    {
      delete_node_with_one_child (&root, &father_of_successor,
                                  successor);
    }
    else
    {
      delete_leaf (&root, &father_of_successor, successor);
    }
  }
  return root;
}

void delete_tree (Node *root)
{
  while (root)
  {
    root = delete_product (root, root->product.name);
  }
}

Node *update_quantity (Node *root, char *name, int amount_to_update)
{
  if (!root || !name)
  {
    fprintf (stderr, "%s%s", ERROR, INVALID_POINTER);
    return root;
  }
  else
  {
    Product *p = search_product (root, name);
    if (p)
    {
      if (amount_to_update >= 0)
      {
        (*p).quantity += amount_to_update;
      }
      else
      {
        (*p).quantity -= abs (amount_to_update);
      }
      if ((p->quantity) == 0)
      {
        delete_product (root, p->name);
      }
      else if ((p->quantity) < 0)
      {
        (*p).quantity += abs (amount_to_update);
        fprintf (stderr, "%s%s", ERROR, INVALID_QUANTITY);
      }
    }
    else
    {
      fprintf (stderr, "%s%s", ERROR, PRODUCT_NOT_FOUND);
    }
  }

  return root;
}