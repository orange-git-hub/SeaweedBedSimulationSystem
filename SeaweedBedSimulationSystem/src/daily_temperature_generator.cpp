/// <summary>
/// Created by 石川澄空 on 25/04/18.
/// 日毎の水温を、月初水温の直線補完で生成するクラス
/// </summary>

#include "daily_temperature_generator.h"

#include <chrono>
#include <iostream>
#include "config_loader.h"
#include "timer.h"
#include <string>

// グローバルインスタンスの定義
daily_temperature_generator global_daily_temperature_generator(
    "/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/simulation_config.yml"
);



// コンストラクタ定義
daily_temperature_generator::daily_temperature_generator(const std::string& config_path)
{

    config_loader config(config_path);

    // 月初水温を取得する
    std::vector<std::string> temp_strings = config.get_list("water_temperature_monthly_data");
    monthly_temperature_array.reserve(temp_strings.size());  // メモリ確保（最適化）

    for (const auto& str : temp_strings) {
        monthly_temperature_array.push_back(std::stod(str));  // std::stod で stringからdouble に変換
    }

    // 月初水温の長さが12でないならエラー
    if (monthly_temperature_array.size() != 12) {
        throw std::runtime_error("[ERROR] Config Data Error: \"config\" --> \"simulation_config\" --> \"water_temperature_monthly_data\"");
    }

    temperature_calculator();
}

// 現在の月の初日の水温と次の月の初日の水温を取得，その日数で線形補完して，その日の水温を取得する．
void daily_temperature_generator::temperature_calculator()
{
    daily_temperature_array.clear(); // 初期化
    for (int m = 0; m < 12;++m)
    {

        double T2;
        double T1 = monthly_temperature_array[m];
        int days_in_month = timer::get_days_in_month(timer::get_year(), m + 1);
        if (m == 11)
        {
            T2 = monthly_temperature_array[0];
        }
        else
        {
            T2 = monthly_temperature_array[m + 1];
        }

        for (int d = 0; d < days_in_month; ++d)
        {
            double interpolated_temp = T1 + (T2 - T1) * (static_cast<double>(d) / days_in_month);
            daily_temperature_array.push_back(interpolated_temp);

        }
    }
}


// mainはこの関数を呼び出して水温を取得する
double daily_temperature_generator::get_temperature() const
{
    return daily_temperature_array[timer::get_yearly_consistent_day()];
}
