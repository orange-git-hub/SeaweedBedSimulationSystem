/// <summary>
/// Created by 石川澄空 on 25/04/16.
/// 生物共通の機能を記述するクラス，Animalクラス，Algaeクラスが継承して用いる．
/// </summary>

#pragma once

#include <string>

class living_thing {
protected:
    int day_age;
    int max_age;
    bool is_breedable;
    bool is_have_breed;
public:
    living_thing(); // コンストラクタ
    virtual ~living_thing() = default;

    void check_is_breedable(int breedable_age, int breedable_month);
    void prohibit_breeding();
    void allow_breeding();
    [[nodiscard]] int get_day_age() const;
    [[nodiscard]] int get_max_age() const;
    [[nodiscard]] bool get_is_breedable() const;
    void update_day_age();
};

// グローバル宣言
extern living_thing global_living_thing;

