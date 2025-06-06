/// <summary>
/// Created by 石川澄空 on 25/04/17.
/// </summary>

#pragma once


#include "living_thing.h"
#include <string>
#include <iostream>

class animal : public living_thing
{
protected:
    double body_weight; // 体重
    double body_length; // 体長
    double feed_conversion_rate{}; // 飼料転換効率
    double feed_value; // 主な摂餌対象の飼料価値
    double feed_amount; // 摂餌量
    double allometric_scaling_coefficient; // 摂餌量を求める関数の係数
    // fish,sea_urchinクラスで個別に実装する純粋仮想関数
    virtual double body_weight_increase_calculator(double water_temperature) = 0; // ある量の摂餌対象を摂餌した時の体重変化量を求める関数
    virtual double feed_amount_calculator() = 0; // 体重と飼料転換効率から摂餌量を求める関数
    virtual double aging_effect(int day_age) = 0; //　年齢が摂餌量に与える影響を求める関数．
    virtual double temperature_effect(double water_temperature) = 0; // 水温が摂餌量に与える影響を求める関数．

public:
    explicit animal(const std::string& config_path); // コンストラクタ
    virtual ~animal() = default; // 仮想ディストラクターの定義

    void body_weight_calculator(); // 微小体重増加量を加算する関数.
    [[nodiscard]] double get_feed_amount() const; // 摂餌量を返す関数.
    [[nodiscard]] double get_body_weight() const; // 体重を返す関数.
};
