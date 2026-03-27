#include "HashMap.hpp"

#ifndef _DICTIONARY_H_
#define _DICTIONARY_H_
#include <string>

class InvalidKey : public std::invalid_argument {
  friend class Dictionary;
 public:
  explicit InvalidKey (const std::string &error_str = "")
      : std::invalid_argument (error_str)
  {}
};

class Dictionary : public HashMap<std::string, std::string> {
 public:
  Dictionary ()= default;
  Dictionary (const std::vector<std::string> &key_vec,
                       const std::vector<std::string> &val_vec) :
      HashMap<std::string, std::string> (key_vec, val_vec)
  {}
  /**
   *
   * @param key key to delete from dictionary
   * @return if key not in dictionary, throws an error.
   * otherwise, returns true if key was erased successfully from the
   * dictionary and false if not.
   */
  bool erase (const std::string &key) override
  {
    if (!HashMap<std::string, std::string>::contains_key (key))
    {
      throw InvalidKey (KEY_NOT_IN_MAP_ERROR);
    }
    return HashMap<std::string, std::string>::erase (key);
  }
  /**
   *
   * @tparam Iterator a template Iterator we can iterate with.
   * @param begin the beginning of the container.
   * @param end the end of the container.
   * the function will add elements in container to the dictionary.
   */
  template<typename Iterator>
  void update (Iterator begin, Iterator end) noexcept
  {
    for (Iterator it = begin; it != end; ++it)
    {
      this->operator[] (it->first) = it->second;
    }
  }

};

#endif //_DICTIONARY_H_
