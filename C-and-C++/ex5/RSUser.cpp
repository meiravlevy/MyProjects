

// don't change those includes
#include "RSUser.h"

#include <utility>
#include "RecommenderSystem.h"

// implement your cpp code here
RSUser::RSUser (std::string name, sp_rec_system sp_rec_sys,
                rank_map rankings) : user_name_ (std::move (name)),
                                     sp_rec_sys_ (std::move (sp_rec_sys)),
                                     user_rank_map_ (std::move (rankings))
{
}

void RSUser::add_movie_to_rs(const std::string &name, int year,
                     const std::vector<double> &features,
                     double rate)
{
  sp_rec_sys_->add_movie (name, year, features);
  user_rank_map_.insert(std::pair<sp_movie,double>(sp_rec_sys_->get_movie
  (name,year), rate));
}

sp_movie RSUser::get_recommendation_by_content () const
{
  return sp_rec_sys_->recommend_by_content (*this);
}

sp_movie RSUser::get_recommendation_by_cf(int k) const
{
  return sp_rec_sys_->recommend_by_cf (*this, k);
}

double RSUser::get_prediction_score_for_movie (const std::string &name,
                                               int year, int k) const
{
  sp_movie movie = sp_rec_sys_->get_movie (name, year);
  return sp_rec_sys_->predict_movie_score (*this, movie, k);
}

std::ostream &operator<< (std::ostream &os, const RSUser &user)
{
  os << "name: " << user.user_name_ << "\n" << (*user.sp_rec_sys_)
     << std::endl;
  return os;
}

