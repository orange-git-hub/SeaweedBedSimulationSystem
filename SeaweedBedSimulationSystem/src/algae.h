/// <summary>
/// Created by 石川澄空 on 25/05/07.
/// </summary>

#pragma once



#include "living_thing.h"
#include <string>
#include <iostream>


class algae : public living_thing
{
private:
	int id;
	double bladelets_number; // 葉状部数
	double bladelets_number_by_light; //光合成による増加葉状部数
	double bladelets_number_by_temperature; //水温による増加葉状部数
	double bladelet_length; // 葉状部長
	double bladelet_area; // 葉状部面積
	double bladelet_aspect_ratio; // 葉状部縦横比
	double most_appropriate_temperature_n; // 葉状部数の成長最適水温
	double under_limit_temperature_n; // 葉状部数の成長可能水温下限
	double upper_limit_temperature_n; // 葉状部数の成長可能水温上限
	double most_appropriate_temperature_l; // 葉状部長の成長最適水温
	double under_limit_temperature_l; // 葉状部長の成長可能水温下限
	double upper_limit_temperature_l; // 葉状部長の成長可能水温上限
	double max_photosynthesis_rate; //最大光合成速度
	double threshold_photosynthesis_rate_ratio; //光補償点を全体の割合で表した値
	double bladelets_number_increase_const_by_light; //葉状部数増加の光合成要素の増加量係数
	double bladelets_number_decrease_const_by_light; //葉状部数増加の光合成要素の減少量係数
	double bladelets_number_increase_const_by_temperature; //葉状部数増加の水温要素の増加量係数
	double bladelets_number_decrease_const_by_temperature; //葉状部数増加の水温要素の減少超係数
	double bladelet_length_increase_const; //葉状部長増加量係数
	double bladelet_length_decrease_const; //葉状部長増加量係数
	double surface_density; //海藻の面密度(湿重量)

	double aging_effect_increase_n(double day_age);
	double aging_effect_decrease_n(double day_age);
	double aging_effect_increase_l(double day_age);
	double aging_effect_decrease_l(double day_age);
	double temperature_effect_n(double water_temperature) const;
	double temperature_effect_l(double water_temperature) const;
	double photon_flux_density_calculator();
	double temperature_effect_to_photosynthesis_rate(double water_temperature);
	double photosynthesis_rate_calculator(double water_temperature);
	void bladelets_number_calculator(double water_temperature);
	void bladelet_length_calculator(double water_temperature);
	void bladelet_area_calculator();

public:
	explicit algae(int id_argument,const std::string& config_path);
	void calculation_executor();
	void consumed_feed_back(double feed_amount);
	void initializer();
	[[nodiscard]] double get_bladelets_number() const; // 葉状部数を返す関数
	[[nodiscard]] double get_bladelet_length() const; // 葉状部長を返す関数
	[[nodiscard]] double get_bladelet_area() const;	// 葉状部面積を返す関数
};
