/// <summary>
/// Created by ishikawasora on 25/05/04.
/// 月初の光量子束密度データから日毎の光量子束密度データを生成するスリプト
/// </summary>


#include "daily_photosynthesis_rate_generator.h"
#include "config_loader.h"
#include "timer.h"
#include <iostream>
#include <stdexcept>
#include <string>


// グローバルインスタンスの定義
daily_photosynthesis_rate_generator global_daily_photosynthesis_rate_generator(
    "/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/simulation_config.yml"
);

daily_photosynthesis_rate_generator::daily_photosynthesis_rate_generator(const std::string& config_path)
{
    config_loader config = config_loader(config_path);

    // stringでデータリストを受け取ってintに変換
    std::vector<std::string> temp_string = config.get_list("global_horizontal_irradiance");
    for (const auto& data : temp_string)
    {
        monthly_global_horizontal_irradiance_array.push_back(std::stod(data));
    }
    // 配列の長さが12出ないならエラー
    if (monthly_global_horizontal_irradiance_array.size() != 12)
    {
        throw std::runtime_error("[ERROR] monthly_global_horizontal_irradiance.size() != 12");
    }
    daily_photosynthesis_rate_calculator();
}

void daily_photosynthesis_rate_generator::daily_photosynthesis_rate_calculator() {
    daily_photosynthesis_rate_array.clear(); // 初期化
    for (int m = 0; m < 12;++m)
    {
        double p2;
        double p1 = monthly_global_horizontal_irradiance_array[m];
        int days_in_month = timer::get_days_in_month(timer::get_year(), m + 1);
        if (m == 11)
        {
            p2 = monthly_global_horizontal_irradiance_array[0];
        }
        else
        {
            p2 = monthly_global_horizontal_irradiance_array[m + 1];
        }

        for (int d = 0; d < days_in_month; ++d)
        {
            //1000000 / 86400は単位変換
            //(0.929 + 2.084) * 全天日射量 = 光量子束密度
            //0.3は水深による減光率

            double interpolated_temp = (1000000 / 86400) * (0.929 + 2.084 * 0.3 * (p1 + (p2 - p1) * (static_cast<double>(d) / days_in_month)));
            daily_photosynthesis_rate_array.push_back(interpolated_temp);
        }
    }
}

// mainはこの関数を呼び出して純光合成量を取得する
double daily_photosynthesis_rate_generator::get_photosynthesis_rate() const
{
    return daily_photosynthesis_rate_array[timer::get_yearly_consistent_day()];
}

