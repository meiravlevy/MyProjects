#ifndef _HASHMAP_HPP_
#define _HASHMAP_HPP_

#include <vector>
#include <functional>
#include <exception>
#include <iostream>
#include <algorithm>
#define HASH_START_CAP 16
#define MULT_CAP 2
#define LOWER_LOAD_FACTOR (double)0.25
#define UPPER_LOAD_FACTOR (double)0.75

#define VECTOR_SIZES_ERROR "ERROR: Keys vector and values vector must be "\
                              "from the same size."
#define KEY_NOT_IN_MAP_ERROR "ERROR: key doesn't exist"

template<typename KeyT, typename ValueT>
class HashMap {
  class ConstIterator;
 public:
  typedef ConstIterator const_iterator;
  typedef std::vector<std::pair<KeyT, ValueT>> vec_of_pairs;

  explicit HashMap () noexcept (false): size_ (0), capacity_
      (HASH_START_CAP), buckets_ (new vec_of_pairs[HASH_START_CAP])
  {}
  /**
   *
   * @param key_vec vector containing keys to insert.
   * @param val_vec vector containing values to insert.
   * this constructor will add at position i a key from key_vec[i] and
   * val_vec[i]. throws an exception if vectors aren't in the same size.
   */
  explicit HashMap (const std::vector<KeyT> &key_vec, const
  std::vector<ValueT> &val_vec) noexcept (false): size_ (0), capacity_
      (HASH_START_CAP), buckets_ (new vec_of_pairs[HASH_START_CAP])
  {
    if (key_vec.size () != val_vec.size ())
    {
      delete[] this->buckets_;
      throw std::domain_error (VECTOR_SIZES_ERROR);
    }
    for (size_t i = 0; i < key_vec.size (); ++i)
    {
      this->operator[] (key_vec[i]) = val_vec[i];
    }
  }

  HashMap (const HashMap &other) noexcept (false) //copy constructor
      : size_ (other.size_), capacity_ (other.capacity_),
        buckets_ (new vec_of_pairs[other.capacity_])
  {
    std::copy (other.buckets_, other.buckets_ + other.capacity_, buckets_);
  }

  virtual ~HashMap ()
  {
    delete[] this->buckets_;
  }
  /**
   *
   * @return number of elements in the hash map.
   */
  int size () const noexcept
  {
    return this->size_;
  }
/**
 *
 * @return maximum number of elements that can be saves in the hash map.
 */
  int capacity () const noexcept
  {
    return this->capacity_;
  }
  /**
   *
   * @return  true if the hash map is empty. false otherwise.
   */
  virtual bool empty () const noexcept
  {
    return (this->size_ == 0);
  }
  /**
 *
 * @param key key to be inserted in the hash map.
 * @param val value to be inserted in the hash map.
 * @return true if the key-value pair were inserted successfully. false if
 * key already exists in the hash map.
 */
  bool insert (const KeyT &key, const ValueT &val) noexcept
  {
    if (this->contains_key (key))
    {
      return false;
    }
    //inserting a pair of key and value to the bucket
    size_t h_index = hash_func (this->capacity_, key);
    this->buckets_[h_index].push_back (std::make_pair (key, val));
    ++this->size_;
    //increasing capacity if needed for rehashing.
    int capacity = this->get_bigger_capacity ();
    if (capacity != this->capacity_)
    {
      try
      { this->re_hash (capacity); }
      catch (const std::exception &e)
      { return false; }
    }
    return true;
  }

  /**
   *
   * @param key key we want to find in the hash map.
   * @return true if key exists in the hash map. false otherwise.
   */
  bool contains_key (const KeyT &key) const noexcept
  {
    size_t key_index = hash_func (this->capacity_, key);
    for (const auto &key_val: this->buckets_[key_index])
    {
      if (key_val.first == key)
      {
        return true;
      }
    }
    return false;
  }
  /**
   *
   * @param key key we want to find in the hash map.
   * @return value associated to the key in hash map. if key doesn't exist,
   * an exception will be thrown.
   */
  ValueT &at (const KeyT &key) noexcept (false)
  {
    size_t key_index = hash_func (this->capacity_, key);
    for (auto &key_val: this->buckets_[key_index])
    {
      if (key_val.first == key)
      {
        return key_val.second;
      }
    }
    throw std::out_of_range (KEY_NOT_IN_MAP_ERROR);
  }
  /**
  *
  * @param key key we want to find in the hash map.
  * @return value associated to the key in hash map. if key doesn't exist,
  * an exception will be thrown.
  */
  const ValueT &at (const KeyT &key) const noexcept (false)
  {
    size_t key_index = hash_func (this->capacity_, key);
    for (const auto &key_val: this->buckets_[key_index])
    {
      if (key_val.first == key)
      {
        return key_val.second;
      }
    }
    throw std::out_of_range (KEY_NOT_IN_MAP_ERROR);
  }

  /**
  *
  * @param key key to erase from hash map.
  * @return true if key was erased. false otherwise.
  */
  virtual bool erase (const KeyT &key)
  {
    if (!this->contains_key (key)) //no key to erase
    { return false; }
    //finding bucket that key is in.
    int bucket_idx = hash_func (this->capacity_, key);
    vec_of_pairs &vec = this->buckets_[bucket_idx];
    //erasing the pair of key and it's value.
    for (auto it = vec.begin (); it != vec.end (); ++it)
    {
      if (it->first == key)
      {
        vec.erase (it);
        --this->size_;
        break;
      }
    }
    //decreasing capacity if needed for rehashing.
    int capacity = this->get_smaller_capacity ();
    if (capacity != this->capacity_)
    {
      try
      { this->re_hash (capacity); }
      catch (const std::exception &e)
      { return false; }
    }
    return true;
  }
  /**
   *
   * @return the load factor of the hash map which is calculated by:
   * (size_of_hash_map/capacity)
   */
  double get_load_factor () const noexcept
  {
    return (double) this->size_ / (double) this->capacity_;
  }
/**
 *
 * @param key will find this key's bucket.
 * @return size of the bucket in which the key is in.
 */
  int bucket_size (const KeyT &key) const noexcept (false)
  {
    int h_index = bucket_index (key);
    return this->buckets_[h_index].size ();
  }
  /**
   *
   * @param key will find this key's bucket.
   * @return index(location) of bucket of key in the hash map.
   */
  int bucket_index (const KeyT &key) const noexcept (false)
  {
    if (this->contains_key (key))
    {
      return (int) hash_func (this->capacity_, key);
    }
    throw (std::out_of_range (KEY_NOT_IN_MAP_ERROR));
  }

  /**
   *
   * @param key will want to return the value associated with this key.
   * @return value associated with this key. if key doesn't exist, we will
   * insert it into the hash map with default value.
   */
  ValueT &operator[] (const KeyT &key) noexcept
  {
    size_t bucket_index = hash_func (this->capacity_, key);
    for (auto &key_val: this->buckets_[bucket_index])
    {
      if (key_val.first == key)
      {
        return key_val.second;
      }
    }
    this->insert (key, ValueT ());
    return this->at (key);
  }
  /**
 *
 * @param key will want to return the value associated with this key.
 * @return value associated with this key. if key doesn't exist, we will
 * insert it into the hash map with default value.
 */
  ValueT operator[] (const KeyT &key) const noexcept
  {
    try
    {
      ValueT val = this->at (key);
      return val;
    }
    catch (const std::out_of_range &e)
    {
      return ValueT ();
    }
  }
  /**
   * this function will clear all the elements in the hash map.
   */
  void clear () noexcept
  {
    for (int i = 0; i < this->capacity_; ++i)
    {
      this->buckets_[i].clear ();
    }
    this->size_ = 0;
  }
  /**
   *
   * @param rhs right hand side of the operator
   * @return the object updated with rhs properties.
   */
  HashMap &operator= (const HashMap<KeyT, ValueT> &rhs)
  {
    if (this != &rhs)
    {
      delete[] this->buckets_;
      this->buckets_ = new vec_of_pairs[rhs.capacity_];
      this->size_ = rhs.size_;
      this->capacity_ = rhs.capacity_;
      std::copy (rhs.buckets_, rhs.buckets_ + capacity_, this->buckets_);
    }
    return *this;
  }
  /**
   *
   * @param rhs hashmap on right hand side of operator to compare with.
   * @return true if hashmaps are equal. false otherwise.
   */
  bool operator== (const HashMap<KeyT, ValueT> &rhs) const
  {
    if (this->size_ != rhs.size_)
    { return false; }
    for (const auto &key_val: *this)
    {
      try
      {
        //checking if values associated with keys are equal in hashmaps.
        if (this->at (key_val.first) != rhs.at (key_val.first))
        { return false; }
      }
      catch (const std::out_of_range &e)
      { return false; }
    }
    return true;
  }
  /**
   *
   * @param rhs hashmap on right hand side of operator to compare with.
   * @return true if hashmaps are not equal. false otherwise.
   */
  bool operator!= (const HashMap<KeyT, ValueT> &rhs) const
  {
    return !(this->operator== (rhs));
  }

  const_iterator cbegin () const
  {
    const_iterator start_it = ConstIterator (*this, 0, 0);
    //we want to start from a bucket that isn't empty.
    if (this->buckets_[0].empty ())
    {
      ++start_it;
    }
    return start_it;
  }

  const_iterator cend () const
  {
    return ConstIterator (*this, this->capacity_, 0);
  }
  const_iterator begin () const
  {
    return cbegin ();
  }
  const_iterator end () const
  {
    return cend ();
  }
 private:
  int size_;
  int capacity_;
  vec_of_pairs *buckets_;
  /**
   *
   * @param key the key we want to hash.
   * @return the index in the hash map to insert key into.
   */
  static std::size_t hash_func (int capacity, KeyT key) noexcept
  {
    std::hash<KeyT> hash_key;
    std::hash<int> int_hash;
    return hash_key (key) & (int_hash (capacity - 1));
  }
  /**
   *
   * @param capacity new capacity for the hash map
   * the function will copy all elements of hash table to a bigger hash table.
   */
  void re_hash (int capacity) noexcept (false)
  {
    auto *re_hashed = new vec_of_pairs[capacity];
    for (auto iter = this->begin (); iter != this->end (); ++iter)
    {
      std::size_t re_hash_idx = hash_func (capacity, iter->first);
      re_hashed[re_hash_idx].push_back (*iter);
    }
    std::swap (this->buckets_, re_hashed);
    delete[] re_hashed;
    this->capacity_ = capacity;
  }
  /**
   *
   * @return a smaller capacity that holds the requirement of:
   * size/capacity < lower load factor
   */
  int get_smaller_capacity () const noexcept
  {
    int capacity = this->capacity ();
    while (capacity > 1 and (double) size_ / (double) capacity <
                            LOWER_LOAD_FACTOR)
    {
      capacity /= MULT_CAP;
    }
    return capacity;
  }
  /**
 *
 * @return a bigger capacity that holds the requirement of:
 * size/capacity > upper load factor
 */
  int get_bigger_capacity () const noexcept
  {
    int capacity = this->capacity ();
    while ((double) size_ / (double) capacity > UPPER_LOAD_FACTOR)
    {
      capacity *= MULT_CAP;
    }
    return capacity;
  }
  class ConstIterator {
    friend class HashMap<KeyT, ValueT>;
   public:
    typedef std::pair<KeyT, ValueT> value_type;
    typedef const value_type &reference;
    typedef const value_type *pointer;
    typedef int difference_type;
    typedef std::forward_iterator_tag iterator_category;

    reference operator* () const noexcept
    {
      return this->hash_map_.buckets_[this->cur_bucket_][this->cur_pair_];
    }
    ConstIterator &operator++ () noexcept
    {
      //if we got to the end of the bucket:
      if ((++this->cur_pair_) >=
          (int) this->hash_map_.buckets_[this->cur_bucket_].size ())
      {
        ++this->cur_bucket_;
        this->cur_pair_ = 0;
      }
      //want to get to a bucket that is not empty:
      while (this->cur_bucket_ != this->hash_map_.capacity_ and
             this->hash_map_.buckets_[this->cur_bucket_].empty ())
      {
        ++this->cur_bucket_;
      }
      return *this;
    }
    ConstIterator operator++ (int) noexcept
    {
      ConstIterator it (*this);
      this->operator++ ();
      return it;
    }
    pointer operator-> () const noexcept
    {
      return &(this->operator* ());
    }
    bool operator== (const ConstIterator &rhs) noexcept
    {
      return ((&(this->hash_map_) == &(rhs.hash_map_))
              and (this->cur_bucket_ == rhs.cur_bucket_)
              and (this->cur_pair_ == rhs.cur_pair_));
    }
    bool operator!= (const ConstIterator &rhs) noexcept
    {
      return !(this->operator== (rhs));
    }

   private:
    const HashMap<KeyT, ValueT> &hash_map_;
    int cur_bucket_;
    int cur_pair_;
    ConstIterator (const HashMap<KeyT, ValueT> &hash_map, int bucket_idx,
                   int pair_index)
        : hash_map_ (hash_map), cur_bucket_ (bucket_idx),
          cur_pair_ (pair_index)
    {}
  };
};
#endif //_HASHMAP_HPP_
