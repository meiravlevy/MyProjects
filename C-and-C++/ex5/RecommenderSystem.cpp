#include "RecommenderSystem.h"

bool sp_movie_year_and_name_comp (const sp_movie &sp_m1, const sp_movie &sp_m2)
{
  return (*sp_m1) < (*sp_m2);
}
bool double_is_bigger_comp (const double &a, const double &b)
{
  return a > b;
}
sp_movie RecommenderSystem::add_movie (const std::string &name, int year, const
std::vector<double> &features)
{
  auto sp_m = std::make_shared<Movie> (Movie (name, year));
  recommend_sys_map_.insert (std::pair<sp_movie, std::vector<double>>
                                 (sp_m, features));
  return sp_m;
}

sp_movie RecommenderSystem::get_movie (const std::string &name, int year) const
{
  auto sp_m = std::make_shared<Movie> (name, year);
  auto itr = recommend_sys_map_.find (sp_m);
  if (itr != recommend_sys_map_.end ())
  {
    return itr->first;
  }
  return sp_movie{nullptr};
}

sp_movie RecommenderSystem::recommend_by_content (const RSUser &user)
{
  rank_map u_rank_map = user.get_ranks ();
  double avg_ranks = get_user_avg_ranks (u_rank_map);
  std::vector<double> preferred_movies
      ((*recommend_sys_map_.begin ()).second.size (), 0);
  make_preference_vec (preferred_movies, u_rank_map, avg_ranks);
  std::pair<sp_movie, double> max_resemblance_movie (nullptr, -1);
  //resemblance of movies to the preference_movies vector:
  for (const auto &movie: recommend_sys_map_)
  {
    //if movie not ranked by user:
    if (u_rank_map.find (movie.first) == u_rank_map.end ())
    {
      double resemblance_of_vecs = calc_resemblance_of_vecs (movie.second,
                                                             preferred_movies);
      if (resemblance_of_vecs > max_resemblance_movie.second)
      {
        max_resemblance_movie.first = movie.first;
        max_resemblance_movie.second = resemblance_of_vecs;
      }

    }
  }
  return max_resemblance_movie.first;
}

double RecommenderSystem::predict_movie_score (const RSUser &user, const
sp_movie &movie, int k)
{
  resemblance_map resemble_map (double_is_bigger_comp);
  rank_map u_rank_map = user.get_ranks ();
  calc_resemble_map (movie, resemble_map, u_rank_map);
  return calc_prediction_movie_score (k, resemble_map, u_rank_map);
}

sp_movie RecommenderSystem::recommend_by_cf (const RSUser &user, int k)
{
  std::pair<sp_movie, double> max_resemblance_movie (nullptr, 0);
  rank_map u_rank_map = user.get_ranks ();
  for (const auto &movie: recommend_sys_map_)
  {
    if (u_rank_map.find (movie.first) == u_rank_map.end ())
    {
      double predicted_movie_score = predict_movie_score (user, movie.first,
                                                          k);
      if (predicted_movie_score > max_resemblance_movie.second)
      {
        max_resemblance_movie.first = movie.first;
        max_resemblance_movie.second = predicted_movie_score;
      }
    }
  }
  return max_resemblance_movie.first;

}
void
RecommenderSystem::calc_resemble_map (const sp_movie &movie,
                                      resemblance_map &resemble_map,
                                      rank_map &u_rank_map)
{
  for (const auto &u_movie: u_rank_map)
  {
    double resemble_movies_angle = calc_resemblance_of_vecs
        (recommend_sys_map_[movie], recommend_sys_map_[u_movie.first]);
    resemble_map.insert (std::pair<double, sp_movie> (resemble_movies_angle,
                                                      u_movie.first));
  }
}

double RecommenderSystem::calc_prediction_movie_score (const int &k, const
resemblance_map &resemble_map, rank_map &u_rank_map)
{
  double numerator_sum_rank = 0;
  double denominator_sum_rank = 0;
  auto cur_iter_resemble_map = resemble_map.begin ();
  for (int i = 0; i < k; i++)
  {
    double angle_resemble = (*cur_iter_resemble_map).first;
    denominator_sum_rank += angle_resemble;
    double u_rank = u_rank_map[(*cur_iter_resemble_map).second];
    numerator_sum_rank += (angle_resemble * u_rank);
    cur_iter_resemble_map++;
  }
  return numerator_sum_rank / denominator_sum_rank;
}

double
RecommenderSystem::get_user_avg_ranks (rank_map &u_rank_map)
{
  double avg_ranks = 0;
  std::for_each (u_rank_map.begin (), u_rank_map.end (), SUM_USER_RANKS);
  avg_ranks /= ((double) u_rank_map.size ());
  return avg_ranks;
}

void RecommenderSystem::make_preference_vec (std::vector<double>
                                              &preferred_movies,
                                             const rank_map &u_rank_map, const
                                              double &avg_ranks)
{
  for (const auto &movie: u_rank_map)
  {
    double new_rank = movie.second -avg_ranks;
    std::vector<double> features = recommend_sys_map_[movie.first];
    for (int i = 0; i < (int)preferred_movies.size(); ++i)
    {
      preferred_movies[i] += (features[i] * new_rank);
    }
  }

}
double
RecommenderSystem::calc_resemblance_of_vecs (const std::vector<double>
                                              &features,
                                             const std::vector<double>
                                                  &pref_vec)
{
  double norm_features = std::sqrt (std::inner_product (features
                                                            .begin (),
                                                        features.end (),
                                                        features.begin (),
                                                        0.0));
  double norm_pref_movie = std::sqrt (std::inner_product (pref_vec.begin (),
                                                          pref_vec.end (),
                                                          pref_vec.begin (),
                                                          0.0));
  double scalar_mult_vecs = std::inner_product (features.begin (),
                                                features.end (),
                                                pref_vec.begin (), 0.0);
  double resemblance_of_vecs = scalar_mult_vecs /
                               (norm_features * norm_pref_movie);
  return resemblance_of_vecs;
}

std::ostream &operator<< (std::ostream &os, const RecommenderSystem &
rec_system)
{
  for (const auto &movie: rec_system.recommend_sys_map_)
  {
    os << (*movie.first);
  }
  return os;
}