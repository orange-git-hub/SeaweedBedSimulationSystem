/// <summary>
/// Created by 石川澄空 on 25/04/22.
/// 魚類の成長を管理するクラス
/// </summary>

#include "fish.h"
#include "animal.h"
#include "living_thing.h"
#include "config_loader.h"
#include "daily_temperature_generator.h"
#include <iostream>
#include <stdexcept>
#include <string>

config_loader config("/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/fish_config.yml");
living_thing living_thing();


fish::fish(int id_argument) : animal("/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/fish_config.yml")
{
	// initial_day_age 読み込み
	try
	{
		day_age = std::stoi(config.get_value("initial_day_age"));
		std::cout << "[DEBUG] 'day_age' fetched: " << day_age << std::endl;
	}
	catch (const std::invalid_argument&)
	{
		throw std::runtime_error("Invalid format for 'initial_day_age': " + config.get_value("initial_day_age"));
	}

	// max_age 読み込み
	try
	{
		max_age = std::stoi(config.get_value("max_age"));
		std::cout << "[DEBUG] 'max_age' fetched: " << max_age << std::endl;
	}
	catch (const std::invalid_argument&)
	{
		throw std::runtime_error("Invalid format for 'max_age': " + config.get_value("max_age"));
	}

	id = id_argument; // fish ID の割り当て
	allometric_scaling_coefficient = std::stod(config.get_value("allometric_scaling_coefficient"));	// アメトロリクススケーリングの係数
}

// 年齢の影響を計算する関数
double fish::aging_effect(int day_age)
{
	double d_day_age = static_cast<double>(day_age);
	double effect = std::stod(config.get_value("sl_growth_const"))*(1331 * exp(-(121 * ((d_day_age / 365) - 361 / 1000)) / 200) / 8) / (1331 * exp(-(121 * (0 - 361 / 1000)) / 200) / 8);
	return effect;
}

// 水温による影響を求める関数
double fish::temperature_effect(double water_temperature)
{
  	double effect;
    // 実際のデータから得られる水温と摂餌量の関係
	if (water_temperature < 23)
    {
        effect = 16 * water_temperature - 16 * 14 + 6;
    }
	else
	{
   		effect = 550 - 400 * exp((- water_temperature + 23) / 5);
    }

    effect = effect / (550 - 400 * exp((- 30 + 23) / 5)); // 最大値である30℃での摂餌率を1として相対値に変換
	return effect;
}

// 体重から摂餌量を求める関数．
double fish::feed_amount_calculator()
{
	//feed_amount = (delta_increase_body_weight - before_day_delta_increase_body_weight) / (feed_value * aging_effect(get_day_age()) * temperature_effect(water_temperature));
	//feed_amount = body_weight / feed_value * aging_effect(get_day_age()) * temperature_effect(water_temperature);
	// アメトロリックスケーリング*水温の影響(要検証)
	feed_amount =  allometric_scaling_coefficient * pow(body_weight ,0.75) * temperature_effect(global_daily_temperature_generator.get_temperature());
	return feed_amount;
}


// ある量の摂餌対象を摂餌した時の体重変化量を求める関数．
double fish::body_weight_increase_calculator(double water_temperature)
{
	delta_increase_body_weight = feed_amount_calculator() * feed_value * aging_effect(get_day_age());
	return delta_increase_body_weight;
}

// 微小増加体重を加算する関数
void animal::body_weight_calculator()
{
	body_weight += body_weight_increase_calculator(global_daily_temperature_generator.get_temperature());
}