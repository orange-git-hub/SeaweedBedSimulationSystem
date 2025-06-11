/// <summary>
/// main
/// </summary>


#include <iostream>
#include <string>
#include <vector>
#include "config_loader.h"
#include "fish.h"
#include "algae.h"
#include "animal.h"
#include "timer.h"
#include "daily_temperature_generator.h"
#include "daily_photosynthesis_rate_generator.h"

timer timer("SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/simulation_config.yml");
int main()
{
    // 計測開始のためのタイマーと設定ファイルの読み込み
    config_loader fish_config("SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/fish_config.yml");
    config_loader algae_config("SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/algae_config.yml");
    config_loader simulation_config("SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/simulation_config.yml");

    // 各生物に増殖を許可するかどうか
    bool is_allow_breeding_fish = std::stoi(simulation_config.get_value("is_allow_breeding_fish"));
    bool is_allow_breeding_algae = std::stoi(simulation_config.get_value("is_allow_breeding_algae"));

    // 初期個体数の取得
    int initial_fish_population = std::stoi(fish_config.get_value("initial_population"));
    int initial_algae_population = std::stoi(algae_config.get_value("initial_population"));

    // 魚の個体とデータ格納用配列
    std::vector<fish> fish_instance_array;
    std::vector<std::vector<double>> feed_amount_array;
    std::vector<std::vector<double>> body_weight_array;

    // 藻類の個体とデータ格納用配列
    std::vector<algae> algae_instance_array;
    std::vector<std::vector<double>> bladelets_number_array;
    std::vector<std::vector<double>> bladelet_length_array;
    std::vector<std::vector<double>> bladelet_area_array;
    std::vector<double> sum_bladelet_area_array;

    // 初期個体数に応じたメモリの確保
    fish_instance_array.reserve(initial_fish_population);
    feed_amount_array.resize(initial_fish_population);
    body_weight_array.resize(initial_fish_population);

    algae_instance_array.reserve(initial_algae_population);
    bladelets_number_array.resize(initial_algae_population);
    bladelet_length_array.resize(initial_algae_population);
    bladelet_area_array.resize(initial_algae_population);
    sum_bladelet_area_array.resize(std::stoi(simulation_config.get_value("simulation_day_range")));

    int current_year = timer::get_year();

    // 各個体に対する魚インスタンス生成
    for (int i = 0; i < initial_fish_population; i++)
    {
        fish_instance_array.emplace_back(i);
    }

    // 各個体に対する藻類インスタンス生成
    for (int i = 0; i < initial_algae_population; i++)
    {
        algae_instance_array.emplace_back(i, "SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/algae_config.yml");
    }

    std::cout << "Success make instance" << std::endl;

    // 環境変数の事前生成
    global_daily_temperature_generator.temperature_calculator();
    global_daily_photosynthesis_rate_generator.daily_photosynthesis_rate_calculator();

    // メインシミュレーションループ（日毎）
    for (int i = 0; i < std::stoi(simulation_config.get_value("simulation_day_range")); i++)
    {
        double sum_feed_amount = 0;

        // 魚投入日以降に成長開始
        if (i > std::stoi(fish_config.get_value("bring_in_day")))
        {
            for (int j = fish_instance_array.size() - 1; j >= 0; --j)
            {
                if (fish_instance_array[j].get_day_age() >= fish_instance_array[j].get_max_age())
                {
                    feed_amount_array.erase(feed_amount_array.begin() + j);
                    body_weight_array.erase(body_weight_array.begin() + j);
                    fish_instance_array.erase(fish_instance_array.begin() + j);
                    continue;
                }

                fish& fish_instance = fish_instance_array[j];

                // 年次繁殖リセット
                if (current_year != timer::get_year())
                {
                    fish_instance.allow_breeding();
                    current_year = timer::get_year();
                }

                // 繁殖条件のチェックと実行
                fish_instance.check_is_breedable(std::stoi(fish_config.get_value("breedable_day_age")), std::stoi(fish_config.get_value("breedable_month")));
                if (fish_instance.get_is_breedable() && is_allow_breeding_fish)
                {
                    int reproduce_number = std::stoi(fish_config.get_value("reproductive_rate"));

                    feed_amount_array.resize(feed_amount_array.size() + reproduce_number);
                    body_weight_array.resize(body_weight_array.size() + reproduce_number);

                    unsigned long current_array_size = fish_instance_array.size();
                    for (int k = 1; k <= reproduce_number; k++)
                    {
                        fish_instance_array.emplace_back(current_array_size + k);
                    }
                }
                fish_instance.prohibit_breeding();

                // 成長データ記録配列のリサイズ
                feed_amount_array[j].resize(fish_instance.get_max_age());
                body_weight_array[j].resize(fish_instance.get_max_age());

                // 成長計算とデータ取得
                fish_instance.body_weight_calculator();
                double feed_amount = fish_instance.get_feed_amount();
                sum_feed_amount += feed_amount;
                feed_amount_array[j][i] = feed_amount;
                body_weight_array[j][i] = fish_instance.get_body_weight();
                fish_instance.update_day_age();
            }
            std::cout << "[DEBUG] Success daily fish calculate" << i << std::endl;
        }

        // 藻類の成長と摂餌の影響計算
        double sum_bladelet_area = 0;

        for (int j = algae_instance_array.size() - 1; j >= 0; --j)
        {
            if ((algae_instance_array[j].get_bladelet_area() <= 0 && algae_instance_array[j].get_day_age() != 0) || algae_instance_array[j].get_day_age() >= algae_instance_array[j].get_max_age())
            {
                std::cout << "[DEBUG] " << algae_instance_array[j].get_day_age() << std::endl;
                std::cout << "[DEBUG] " << algae_instance_array[j].get_bladelet_area() << std::endl;
                bladelets_number_array.erase(bladelets_number_array.begin() + j);
                bladelet_length_array.erase(bladelet_length_array.begin() + j);
                bladelet_area_array.erase(bladelet_area_array.begin() + j);
                algae_instance_array.erase(algae_instance_array.begin() + j);

                continue;
            }

            algae& algae_instance = algae_instance_array[j];

            if (current_year != timer::get_year())
            {
                for (auto& algae_instance : algae_instance_array)
                {
                    algae_instance.allow_breeding();
                }
                current_year = timer::get_year();
            }


            algae_instance.check_is_breedable(std::stoi(algae_config.get_value("breedable_day_age")), std::stoi(algae_config.get_value("breedable_month")));
            if (algae_instance.get_is_breedable() && is_allow_breeding_algae)
            {
                int reproduce_number = std::stoi(algae_config.get_value("reproductive_rate"));

                bladelets_number_array.resize(bladelets_number_array.size() + reproduce_number);
                bladelet_length_array.resize(bladelet_length_array.size() + reproduce_number);
                bladelet_area_array.resize(bladelet_area_array.size() + reproduce_number);

                unsigned long current_array_size = algae_instance_array.size();
                for (int k = 1; k <= reproduce_number; k++)
                {
                    algae_instance_array.emplace_back(current_array_size + k, "SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/algae_config.yml");
                    //algae_instance_array[algae_instance_array.size() - 1].initializer(); // インスタンス化したときにコンストラクタが正しく動作していない可能性があるため一時的に初期化関数を用いる。
                    std::cout << "[DEBUG] Success make new algae instance" << std::endl;
                }
                algae_instance.prohibit_breeding();
            }

            algae_instance.calculation_executor();
            algae_instance.consumed_feed_back(sum_feed_amount / static_cast<double>(algae_instance_array.size()));

            double bladelet_area = algae_instance.get_bladelet_area();
            sum_bladelet_area += bladelet_area;

            bladelets_number_array[j].resize(algae_instance.get_max_age());
            bladelet_length_array[j].resize(algae_instance.get_max_age());
            bladelet_area_array[j].resize(algae_instance.get_max_age());

            bladelets_number_array[j][algae_instance.get_day_age()] = algae_instance.get_bladelets_number();
            bladelet_length_array[j][algae_instance.get_day_age()] = algae_instance.get_bladelet_length();
            bladelet_area_array[j][algae_instance.get_day_age()] = algae_instance.get_bladelet_area();

            algae_instance.update_day_age();
        }

        sum_bladelet_area_array[i] = sum_bladelet_area;
        timer::date_counter();
        std::cout << "[DEBUG] Success daily algae calculate" << i << std::endl;
        std::cout << "[test data] " << algae_instance_array.size() << std::endl;
    }

    std::cout << "[DEBUG] Success calculate" << std::endl;

    // 結果出力

    std::cout << "[next data]\n[title] feed amount change\n[x_label] age[day]\n[y_label] feed amount[wet weight/kg/day]" << std::endl;
    for (int i = 0; i < std::stoi(fish_config.get_value("max_age")); i++)
        std::cout << "[data] " << feed_amount_array[0][i] << std::endl;

    std::cout << "[next data]\n[title] body weight change\n[x_label] age[day]\n[y_label] body weight[g]" << std::endl;
    for (int i = 0; i < std::stoi(fish_config.get_value("max_age")); i++)
        std::cout << "[data] " << body_weight_array[0][i] << std::endl;

    std::cout << "[next data]\n[title] bladelet number change\n[x_label] age[day]\n[y_label] bladelet number[number]" << std::endl;
    for (int i = 0; i < std::stoi(algae_config.get_value("max_age")); i++)
        std::cout << "[data] " << bladelets_number_array[30][i] << std::endl;

    std::cout << "[next data]\n[title] bladelet length change\n[x_label] age[day]\n[y_label] bladelet length[cm]" << std::endl;
    for (int i = 0; i < std::stoi(algae_config.get_value("max_age")); i++)
        std::cout << "[data] " << bladelet_length_array[30][i] << std::endl;

    std::cout << "[next data]\n[title] bladelet area change\n[x_label] age[day]\n[y_label] bladelet area[cm^2]" << std::endl;
    for (int i = 0; i < std::stoi(algae_config.get_value("max_age")); i++)
        std::cout << "[data] " << bladelet_area_array[30][i] << std::endl;

    std::cout << "[next data]\n[title] sum bladelet area change\n[x_label] age[day]\n[y_label] bladelet area[cm^2]" << std::endl;
    for (double area : sum_bladelet_area_array)
        std::cout << "[data] " << area << std::endl;

    return 0;
}
