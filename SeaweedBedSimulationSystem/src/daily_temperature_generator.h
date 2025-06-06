/// <summary>
/// Created by 石川澄空 on 25/04/18.
/// 月初水温から日次水温を線形的に生成するためのスクリプト
/// </summary>

#pragma once



# include <vector>
# include <string>

class daily_temperature_generator
{
private:

    //std::vector<std::string> monthly_temperature_array;// configファイルから取得した月次水温配列を保持する動的配列
    //double monthly_temperature_array[12] = {14,14.5,16.7,18.4,20.5,22.2,24.8,23.9,22.3,19,16.5,15.5};
    std::vector<double> monthly_temperature_array;
    std::vector<double> daily_temperature_array;
    // 日次水温を計算する関数
public:

    void temperature_calculator();
    explicit daily_temperature_generator(const std::string& config_path);//　コンストラクタ
    [[nodiscard]] double get_temperature() const;

};
extern daily_temperature_generator global_daily_temperature_generator;




