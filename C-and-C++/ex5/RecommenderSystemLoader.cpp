#include "RecommenderSystemLoader.h"

std::unique_ptr<RecommenderSystem>
RecommenderSystemLoader::create_rs_from_movies_file
    (const std::string &movies_file_path) noexcept (false)
{
  std::ifstream movies_file (movies_file_path, std::ios::in);
  if (!movies_file)
  {
    throw std::invalid_argument (FILE_ERROR);
  }
  auto sp_recommend_sys = std::make_unique<RecommenderSystem> ();
  std::string line;
  while (std::getline (movies_file, line))
  {
    std::string movie_name;
    int year;
    std::vector<double> features;
    std::istringstream iss (line);
    parse_m_name_and_year (iss, movie_name, year);
    parse_scores (iss, features);
    sp_recommend_sys->add_movie (movie_name, year, features);
  }
  return sp_recommend_sys;
}

void RecommenderSystemLoader::parse_m_name_and_year
    (std::istringstream &
    iss, std::string &name, int &year)
{
  std::string movie_and_year;
  iss >> movie_and_year;
  name = movie_and_year.substr (0, movie_and_year.find
      (DELIMITER));
  year = std::stoi (movie_and_year.substr ((movie_and_year.find
      (DELIMITER)) + 1));
}

void RecommenderSystemLoader::parse_scores (std::istringstream &iss,
                                            std::vector<double> &
                                            features)
{
  double feature;
  while (iss >> feature)
  {
    if (feature < MIN_SCORE or feature > MAX_SCORE)
    {
      throw std::invalid_argument (SCORE_ERROR);
    }
    features.push_back (feature);
  }
}
