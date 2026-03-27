#include "RSUsersLoader.h"

std::vector<RSUser> RSUsersLoader::create_users_from_file (const std::string &
users_file_path, std::unique_ptr<RecommenderSystem> rs) noexcept (false)
{
  std::ifstream users_file (users_file_path, std::ios::in);
  if (!users_file)
  {
    throw std::invalid_argument (FILE_ERROR);
  }
  std::shared_ptr<RecommenderSystem> sp_rs = std::move (rs);
  std::vector<RSUser> users_vec;
  std::vector<sp_movie> sp_m_vec;
  std::string line;
  std::getline (users_file, line);
  parse_first_line (line, sp_rs,sp_m_vec);
  std::string user_name;
  while (std::getline (users_file, line))
  {
    auto iter_sp_m_vec = sp_m_vec.begin (); //will iterate together with
    // rankings for every user.
    std::istringstream iss (line);
    rank_map user_ranks (0, sp_movie_hash, sp_movie_equal);
    std::string str_score;
    //parse user:
    iss >> user_name;
    while (iss >> str_score)
    {
      if (str_score == NA)
      {
        iter_sp_m_vec++;
        continue;
      }
      double score = std::stod (str_score);
      if (score < MIN_SCORE or score > MAX_SCORE)
      {
        throw std::invalid_argument (SCORE_ERROR);
      }
      user_ranks.insert (std::pair<sp_movie, double> (*iter_sp_m_vec, score));
      iter_sp_m_vec++;
    }
    users_vec.emplace_back (RSUser (user_name, sp_rs, user_ranks));
  }
  return users_vec;
}

void RSUsersLoader::parse_first_line(std::string& line,
                      const std::shared_ptr<RecommenderSystem>& sp_rs,
                      std::vector<sp_movie>& sp_m_vec)
{
  std::istringstream iss (line);
  std::string movie_and_year;
  while (iss >> movie_and_year)
  {
    std::string movie_name;
    int year = 0;
    parse_m_name_and_year (movie_and_year, movie_name, year);
    sp_movie sp_m = sp_rs->get_movie (movie_name, year);
    sp_m_vec.push_back (sp_m);
  }

}



void RSUsersLoader::parse_m_name_and_year
    (std::string &movie_and_year, std::string &name, int &year)
{
  name = movie_and_year.substr (0, movie_and_year.find (DELIMITER));
  year = std::stoi (movie_and_year.substr ((movie_and_year.find
      (DELIMITER)) + 1));
}
