
#ifndef RECOMMENDERSYSTEMLOADER_H
#define RECOMMENDERSYSTEMLOADER_H

#include "RecommenderSystem.h"

#include <fstream>
#include <sstream>
#include <exception>

#define FILE_ERROR "ERROR: file is invalid."
#define SCORE_ERROR "ERROR: invalid score."
#define DELIMITER '-'
#define MIN_SCORE 1
#define MAX_SCORE 10
class RecommenderSystemLoader {

 private:

 public:
  RecommenderSystemLoader () = delete;
  /**
   * loads movies by the given format for movies with their feature's score
   * @param movies_file_path a path to the file of the movies
   * @return smart pointer to a RecommenderSystem which was created with
   * those movies
   */
  static std::unique_ptr<RecommenderSystem> create_rs_from_movies_file
      (const std::string &movies_file_path) noexcept (false);
 private:
  /**
   *
   * @param iss istringstream that we will  read from
   * @param name name of the movie
   * @param year year movie was produced.
   */
  static void parse_m_name_and_year (std::istringstream &iss, std::string
  &name, int &year);
  /**
   *
   * @param iss istringstream that we will  read from
   * @param features the features of the movie.
   */
  static void parse_scores (std::istringstream &iss, std::vector<double> &
  features);
};

#endif //RECOMMENDERSYSTEMLOADER_H
