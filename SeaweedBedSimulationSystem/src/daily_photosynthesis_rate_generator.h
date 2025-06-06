/// <summary>
/// Created by owner on 25/05/04.
/// 月初の光量子束密度データから日毎の光量子束密度データを生成するスリプト
/// </summary>

#pragma once



#include <vector>

class daily_photosynthesis_rate_generator {
private:
    std::vector<double> monthly_global_horizontal_irradiance_array;
    std::vector<double> daily_photosynthesis_rate_array;
public:
    explicit daily_photosynthesis_rate_generator(const std::string& config_path);
    void daily_photosynthesis_rate_calculator();
    [[nodiscard]] double get_photosynthesis_rate() const;
};
extern daily_photosynthesis_rate_generator global_daily_photosynthesis_rate_generator;
