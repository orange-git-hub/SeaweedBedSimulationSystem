/// <summary>
/// Created by 石川澄空 on 25/04/16.
/// 生物共通の機能を記述するクラス，Animalクラス，Algaeクラスが継承して用いる．
/// </summary>

#include "living_thing.h"

#include <iostream>
#include <ostream>

#include "timer.h"

living_thing global_living_thing; // グローバル実体の定義


// 年齢を1日分更新する関数定義
living_thing::living_thing()
{
    day_age = 0;
    max_age = 1875;  // 仮の初期値
    is_breedable = false;
    is_have_breed = false;
}


void living_thing::update_day_age() {
    day_age = day_age + 1;
}

void living_thing::check_is_breedable(int breedable_age, int breedable_month)
{
    if (breedable_age <= day_age && !is_have_breed && breedable_month == timer::get_month())
    {
        std::cout << is_have_breed << std::endl;
        std::cout << "breedable" << day_age <<std::endl;
        is_breedable = true;
    }
    else
    {
        is_breedable = false;
    }
}

void living_thing::prohibit_breeding()
{
    is_have_breed = true;
}

void living_thing::allow_breeding()
{
    is_have_breed = false;
}


bool living_thing::get_is_breedable() const
{
    return is_breedable;
}

int living_thing::get_day_age() const
{
    return day_age;
}

int living_thing::get_max_age() const
{
    return max_age;
}
