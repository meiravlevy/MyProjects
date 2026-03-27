//
// Created on 2/20/2022.
//

#ifndef RECOMMENDERSYSTEM_H
#define RECOMMENDERSYSTEM_H
#include "RSUser.h"

#include <map>
#include <algorithm>
#include <numeric>
#include <cmath>

#define SUM_USER_RANKS [&avg_ranks]\
  (const std::pair<sp_movie,double> &movie)\
  {avg_ranks+= movie.second;}
bool
sp_movie_year_and_name_comp (const sp_movie &sp_m1, const sp_movie &sp_m2);
bool double_is_bigger_comp (const double &a, const double &b);
typedef std::map<double, sp_movie, decltype (double_is_bigger_comp) *>
    resemblance_map;

class RecommenderSystem {
 public:

  explicit RecommenderSystem () : recommend_sys_map_
                                      (sp_movie_year_and_name_comp)
  {};
  /**
   * adds a new movie to the system
   * @param name name of movie
   * @param year year it was made
   * @param features features for movie
   * @return shared pointer for movie in system
   */
  sp_movie
  add_movie (const std::string &name, int year, const std::vector<double>
      &features);

  /**
   * a function that calculates the movie with highest score based on movie
   * features
   * @param ranks user ranking to use for algorithm
   * @return shared pointer to movie in system
   */
  sp_movie recommend_by_content (const RSUser &user);

  /**
   * a function that calculates the movie with highest predicted score based on
   * ranking of other movies
   * @param ranks user ranking to use for algorithm
   * @param k
   * @return shared pointer to movie in system
   */
  sp_movie recommend_by_cf (const RSUser &user, int k);

  /**
   * Predict a user rating for a movie given argument using item cf procedure
   * with k most similar movies.
   * @param user_rankings: ranking to use
   * @param movie: movie to predict
   * @param k:
   * @return score based on algorithm as described in pdf
   */
  double predict_movie_score (const RSUser &user, const sp_movie &movie,
                              int k);

  /**
   * gets a shared pointer to movie in system
   * @param name name of movie
   * @param year year movie was made
   * @return shared pointer to movie in system
   */
  sp_movie get_movie (const std::string &name, int year) const;

  // TODO operator<<
  friend std::ostream &operator<< (std::ostream &os, const RecommenderSystem &
  rec_system);
 private:
  std::map<sp_movie, std::vector<double>,
      decltype (sp_movie_year_and_name_comp) *> recommend_sys_map_;
  /**
   *
   * @param u_rank_map user's rankings
   * @return average of the user's rankings.
   */
  static double get_user_avg_ranks (rank_map &u_rank_map);
  /**
   *
   * @param preferred_movies will be updated according to the formula given
   * of preference vector.
   * @param u_rank_map user's rsnkings.
   * @param avg_ranks the average of user's rankings.
   */
  void make_preference_vec (std::vector<double> &preferred_movies,
                            const rank_map
  &u_rank_map, const double &avg_ranks);
  /**
   *
   * @param features the features of the movie.
   * @param pref_vec the preference vector of the user.
   * @return the resemblance of the vectors calculated by the formula given.
   */
  static double calc_resemblance_of_vecs (const std::vector<double> &features,
                                          const std::vector<double> &pref_vec);
  /**
   *
   * @param movie the movie that we want to see resemblance for
   * @param resemble_map map that will be updated to have all movies and
   * their resemblance to the movie given
   * @param u_rank_map users rankings to calc resemblance to the movie given.
   */
  void
  calc_resemble_map (const sp_movie &movie, resemblance_map &resemble_map,
                     rank_map &u_rank_map);
  /**
   *
   * @param k number of movies in user rank_map that are most s
   * @param resemble_map has the resemblance of each movie that user didn't
   * rank to a given movie that user did rank.
   * @param u_rank_map rankings of user to movies.
   * @return the predicted ranking of the user to the movie.
   */
  static double calc_prediction_movie_score (const int &k, const
  resemblance_map &resemble_map, rank_map &u_rank_map);
};

#endif //RECOMMENDERSYSTEM_H
