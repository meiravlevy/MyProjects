//
// Created on 2/21/2022.
//




#ifndef USERFACTORY_H
#define USERFACTORY_H
#include "RecommenderSystemLoader.h"
#include <cmath>

#define NA "NA"
class RSUsersLoader {
 private:

 public:
  RSUsersLoader () = delete;
  /**
   *
   * loads users by the given format with their movie's ranks
   * @param users_file_path a path to the file of the users and their movie
   * ranks
   * @param rs RecommendingSystem for the Users
   * @return vector of the users created according to the file
   */
  static std::vector<RSUser> create_users_from_file (const std::string &
  users_file_path, std::unique_ptr<RecommenderSystem> rs) noexcept (false);
 private:
  /**
   *
   * @param movie_and_year a string that has movie_name-year.
   * @param name movie name to be updated.
   * @param year year movie was produced to update.
   */
  static void parse_m_name_and_year (std::string &movie_and_year,
                                     std::string &name, int &year);
  /**
   *
   * @param line line to parse from
   * @param sp_rs shared pointer to recommender system
   * @param sp_m_vec vector that will be updated to have shared pointers to
   * movies in file.
   */
  static void parse_first_line (std::string &line,
                                const std::shared_ptr<RecommenderSystem>&sp_rs,
                                std::vector<sp_movie> &sp_m_vec);

};

#endif //USERFACTORY_H
