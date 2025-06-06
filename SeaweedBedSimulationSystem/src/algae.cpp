/// <summary>
/// Created by 石川澄空 on 25/05/07.
/// 藻類の成長を管理するクラス
/// </summary>

#include "algae.h"
#include "living_thing.h"
#include "config_loader.h"
#include <string>
#include "daily_photosynthesis_rate_generator.h"
#include "timer.h"
#include "daily_temperature_generator.h"

config_loader simulation_config = config_loader("/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/simulation_config.yml");
config_loader algae_config = config_loader("/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/algae_config.yml");
daily_photosynthesis_rate_generator photosynthesis_rate_generator = daily_photosynthesis_rate_generator("/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/simulation_config.yml");
daily_temperature_generator daily_temperature_generator("/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/simulation_config.yml");
living_thing living_thing();


algae::algae(int id_argument, const std::string& config_path)
{
	day_age = std::stoi(algae_config.get_value("initial_day_age"));
	max_age = std::stoi(algae_config.get_value("max_age"));
	id = id_argument;
	bladelets_number = std::stod(algae_config.get_value("initial_bladelets_number"));
	bladelets_number_by_light = std::stod(algae_config.get_value("initial_bladelets_number_by_light"));
	bladelets_number_by_temperature = std::stod(algae_config.get_value("initial_bladelets_number_by_temperature"));
	bladelet_length = std::stod(algae_config.get_value("initial_bladelet_length"));
	bladelet_aspect_ratio = std::stod(algae_config.get_value("bladelet_aspect_ratio"));
	most_appropriate_temperature_n = std::stod(algae_config.get_value("most_appropriate_temperature_n"));
	under_limit_temperature_n = std::stod(algae_config.get_value("under_limit_temperature_n"));
	upper_limit_temperature_n = std::stod(algae_config.get_value("upper_limit_temperature_n"));
	most_appropriate_temperature_l = std::stod(algae_config.get_value("most_appropriate_temperature_l"));
	under_limit_temperature_l = std::stod(algae_config.get_value("under_limit_temperature_l"));
	upper_limit_temperature_l = std::stod(algae_config.get_value("upper_limit_temperature_l"));
	max_photosynthesis_rate = std::stod(algae_config.get_value("max_photosynthesis_rate"));
	threshold_photosynthesis_rate_ratio = std::stod(algae_config.get_value("threshold_photosynthesis_rate_ratio"));
	bladelets_number_decrease_const_by_light = std::stod(algae_config.get_value("bladelets_number_decrease_const_by_light"));
	bladelets_number_decrease_const_by_temperature = std::stod(algae_config.get_value("bladelets_number_decrease_const_by_temperature"));
	bladelets_number_increase_const_by_light = std::stod(algae_config.get_value("bladelets_number_increase_const_by_light"));
	bladelets_number_increase_const_by_temperature = std::stod(algae_config.get_value("bladelets_number_increase_const_by_temperature"));
	bladelet_length_increase_const = std::stod(algae_config.get_value("bladelet_length_increase_const"));
	bladelet_length_decrease_const = std::stod(algae_config.get_value("bladelet_length_decrease_const"));
	surface_density = std::stod(algae_config.get_value("surface_density"));
	bladelet_area = bladelet_length * bladelet_aspect_ratio * bladelets_number;
}

void algae::initializer()
{
	day_age = std::stoi(algae_config.get_value("initial_day_age"));
	bladelets_number = std::stod(algae_config.get_value("initial_bladelets_number"));
	bladelets_number_by_light = std::stod(algae_config.get_value("initial_bladelets_number_by_light"));
	bladelets_number_by_temperature = std::stod(algae_config.get_value("initial_bladelets_number_by_temperature"));
	bladelet_length = std::stod(algae_config.get_value("initial_bladelet_length"));
	threshold_photosynthesis_rate_ratio = std::stod(algae_config.get_value("threshold_photosynthesis_rate_ratio"));
	bladelets_number_decrease_const_by_light = std::stod(algae_config.get_value("bladelets_number_decrease_const_by_light"));
	bladelets_number_decrease_const_by_temperature = std::stod(algae_config.get_value("bladelets_number_decrease_const_by_temperature"));
	bladelets_number_increase_const_by_light = std::stod(algae_config.get_value("bladelets_number_increase_const_by_light"));
	bladelets_number_increase_const_by_temperature = std::stod(algae_config.get_value("bladelets_number_increase_const_by_temperature"));
	bladelet_length_increase_const = std::stod(algae_config.get_value("bladelet_length_increase_const"));
	bladelet_length_decrease_const = std::stod(algae_config.get_value("bladelet_length_decrease_const"));
	surface_density = std::stod(algae_config.get_value("surface_density"));
	bladelet_area = bladelet_length * bladelet_aspect_ratio * bladelets_number;
}

double algae::aging_effect_increase_n(double day_age)
{
	double effect;
	if (day_age / 365 < 2.0)
	{
		effect = (day_age / 365) * 0.25 + 0.1;
	}
	else
	{
		effect = 1.0;
	}
	return effect;
}

double algae::aging_effect_decrease_n(double day_age)
{
	double effect;
	if (day_age / 365 < 2.0)
	{
		effect = (1.0 / 7.0) * (day_age / 365);
	}
	else
	{
		effect = 1;
	}
	return effect;
}

double algae::aging_effect_increase_l(double day_age)
{
	double effect;
	double tau = 1.5;
	effect = 0.6*(1 - exp(-tau * (day_age / 365))) + 0.4;
	return effect;
}

double algae::aging_effect_decrease_l(double day_age)
{
	double effect;
	double tau = 50;
	effect = 1 / (2 + exp(-tau * ((day_age / 365) - 2))) + 0.5;
	return effect;
}

double algae::temperature_effect_n(double water_temperature) const
{
	double effect;

	if (water_temperature < under_limit_temperature_n)
	{
		effect = -1;
	}
	else if (water_temperature == under_limit_temperature_n)
	{
		effect = 0;
	}
	else if (water_temperature <= most_appropriate_temperature_n)
	{
		effect = (1 / (most_appropriate_temperature_n - under_limit_temperature_n)) * water_temperature - (1 / (most_appropriate_temperature_n - under_limit_temperature_n)) * under_limit_temperature_n;
	}
	else if (water_temperature <= upper_limit_temperature_n)
	{
		effect = -(1 / (upper_limit_temperature_n - most_appropriate_temperature_n)) * water_temperature + (1 / (upper_limit_temperature_n - most_appropriate_temperature_n)) * upper_limit_temperature_n;
	}
	else
	{
		effect = -(1 / (upper_limit_temperature_n - most_appropriate_temperature_n)) * water_temperature + (1 / (upper_limit_temperature_n - most_appropriate_temperature_n)) * upper_limit_temperature_n;
	}
	if (effect < -1)
	{
		effect = -1;
	}
	return effect;
}

double algae::temperature_effect_l(double water_temperature) const
{
	double effect;
	if (water_temperature < under_limit_temperature_l)
	{
		effect = -1;
	}
	else if (water_temperature == under_limit_temperature_l)
	{
		effect = 0;
	}
	else if (water_temperature <= most_appropriate_temperature_l)
	{
		effect = (1 / (most_appropriate_temperature_l - under_limit_temperature_l)) * water_temperature - (1 / (most_appropriate_temperature_l - under_limit_temperature_l)) * under_limit_temperature_l;
	}
	else if (water_temperature <= upper_limit_temperature_l)
	{
		effect = -(1 / (upper_limit_temperature_l - most_appropriate_temperature_l)) * water_temperature + (1 / (upper_limit_temperature_l - most_appropriate_temperature_l)) * upper_limit_temperature_l;
	}
	else
	{
		effect = (-water_temperature + upper_limit_temperature_l) / 19;
	}
	if (effect < -1)
	{
		effect = -1;
	}
	return effect;
}

// 全天日射量を光量子束密度に変換する関数
double algae::photon_flux_density_calculator()
{
	double daily_photosynthesis_rate = global_daily_photosynthesis_rate_generator.get_photosynthesis_rate();

	return daily_photosynthesis_rate;
}

// 水温が光合成に与える影響を考慮する関数
double algae::temperature_effect_to_photosynthesis_rate(double water_temperature)
{
	auto calculate_effect = [water_temperature](int month) -> double {
		switch (month)
		{
		case 1:
			return -8.172008 + 5.9475548 * water_temperature + -0.12081204 * pow(water_temperature, 2) + 5;
		case 2:
			return -5.5273767 + 4.5903683666667 * water_temperature + -0.0870333737 * pow(water_temperature, 2) + 5;
		case 3:
			return -2.8827454 + 3.3410763333333 * water_temperature + -0.0532547073 * pow(water_temperature, 2) + 5;
		case 4:
			return -0.2381141 + 2.0917843 * water_temperature + -0.019476041 * pow(water_temperature, 2) + 5;
		case 5:
			return -2.3357280666667 + 2.2017631 * water_temperature + -0.023909746 * pow(water_temperature, 2) + 5;
		case 6:
			return -4.4333420333333 + 2.3117419 * water_temperature + -0.028343451 * pow(water_temperature, 2) + 5;
		case 7:
			return -6.530956 + 2.7753556333333 * water_temperature + -0.032777156 * pow(water_temperature, 2) + 5;
		case 8:
			return -3.9674022 + 3.0111122555555 * water_temperature + -0.039660365 * pow(water_temperature, 2) + 5;
		case 9:
			return -1.4038484 + 3.1289905666667 * water_temperature + -0.046543574 * pow(water_temperature, 2) + 5;
		case 10:
			return 1.1597054 + 3.4826255 * water_temperature + -0.053426783 * pow(water_temperature, 2) + 5;
		case 11:
			return -1.9508657333333 + 4.3042686 * water_temperature + -0.0758885353333 * pow(water_temperature, 2) + 5;
		case 12:
			return -8.172008 + 5.1259117 * water_temperature + -0.0983502876667 * pow(water_temperature, 2) + 5;
		default:
			throw std::runtime_error("Invalid month: " + std::to_string(month));
		}
	};

	int month = timer::get_month();
	int next_month = (month % 12) + 1;

	int day = timer::get_day();
	int days_in_month = timer::get_days_in_month(timer::get_year(), month);

	double effect_this_month = calculate_effect(month);
	double effect_next_month = calculate_effect(next_month);

	// 線形補間: 現在の日を使って今月と来月の effect を補間
	double t = static_cast<double>(day) / static_cast<double>(days_in_month);
	double interpolated_effect = (1.0 - t) * effect_this_month + t * effect_next_month;

	return interpolated_effect;
}

// 純光合成量を計算する関数
double algae::photosynthesis_rate_calculator(double water_temperature)
{
	double temperature_effect = temperature_effect_to_photosynthesis_rate(water_temperature);
	double photon_flux_density = photon_flux_density_calculator();
	double photosynthesis_rate = -temperature_effect * exp(-photon_flux_density / (1.6 * temperature_effect)) + temperature_effect - (temperature_effect / 10);

	return photosynthesis_rate;
}

void algae::bladelets_number_calculator(double water_temperature)
{
	// 日照量による成長の計算
	double growth_ratio_by_light = (photosynthesis_rate_calculator(water_temperature) / max_photosynthesis_rate) - threshold_photosynthesis_rate_ratio;

	if (growth_ratio_by_light >= 0)
	{
		bladelets_number_by_light += bladelets_number_increase_const_by_light * growth_ratio_by_light * aging_effect_increase_n(static_cast<double>(get_day_age()));
	}
	else
	{
		bladelets_number_by_light += bladelets_number_decrease_const_by_light * growth_ratio_by_light * aging_effect_decrease_n(static_cast<double>(get_day_age()));
	}
	if (bladelets_number_by_light < 0)
	{
		bladelets_number_by_light = 0;
	}
	// 水温による成長の計算
	double growth_ratio_by_temperature = temperature_effect_n(water_temperature);
	if (growth_ratio_by_temperature >= 0)
	{
		bladelets_number_by_temperature += bladelets_number_increase_const_by_temperature * growth_ratio_by_temperature * aging_effect_increase_n(static_cast<double>(get_day_age()));
	}
	else
	{
		bladelets_number_by_temperature += bladelets_number_decrease_const_by_temperature * growth_ratio_by_temperature * aging_effect_decrease_n(static_cast<double>(get_day_age()));
	}
	if (bladelets_number_by_temperature < 0)
	{
		bladelets_number_by_temperature = 0;
	}

	bladelets_number = bladelets_number_by_light + bladelets_number_by_temperature;
}

 void algae::bladelet_length_calculator(double water_temperature)
{

	if (under_limit_temperature_l <= water_temperature && water_temperature <= upper_limit_temperature_l)
	{
		bladelet_length += bladelet_length_increase_const * temperature_effect_l(water_temperature) * aging_effect_increase_l(get_day_age());
	}
	else
	{
		bladelet_length += bladelet_length_decrease_const * temperature_effect_l(water_temperature) * aging_effect_decrease_l(get_day_age());
	}
	if (bladelet_length < 0)
	{
		bladelet_length = 0;
	}
}

void algae::bladelet_area_calculator()
{
	bladelet_area = bladelet_length * bladelet_aspect_ratio * bladelets_number;
}

void algae::calculation_executor()
{
	bladelets_number_calculator(global_daily_temperature_generator.get_temperature());
	bladelet_length_calculator(global_daily_temperature_generator.get_temperature());
	bladelet_area_calculator();
}

void algae::consumed_feed_back(double feed_amount)
{
	double feed_area = feed_amount / surface_density;
	double feed_length = feed_area / (bladelets_number * bladelet_aspect_ratio * bladelet_length * bladelet_length);
	double feed_number = feed_area / (bladelet_aspect_ratio * bladelet_length * bladelet_length);
	bladelet_length -= feed_length;
	if (bladelet_length < 0)
	{
		bladelet_length = 0;
	}
	bladelets_number -= feed_number;
	if (bladelets_number < 0)
	{
		bladelets_number = 0;
	}
}


double algae::get_bladelets_number() const
{
	return bladelets_number;
}

double algae::get_bladelet_length() const
{

	return bladelet_length;
}

double algae::get_bladelet_area() const
{

	return bladelet_area;
}

