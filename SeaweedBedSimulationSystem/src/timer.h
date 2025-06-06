//
// Created by 石川澄空 on 25/04/16.
//

#ifndef TIMER_H
#define TIMER_H



#include <string>

class timer {
private:
    int static year;
    int static month;
    int static day;
    int static yearly_consistent_day;
    int static consistent_day;
    static bool check_is_leap_year(int check_year);
    void static decide_days_in_month(int check_year, int check_month);

public:
    explicit timer(const std::string& config_path); // 構成ファイルから初期化するコンストラクタ
    int static days_in_month;
    // 現在の日付を返す関数群
    [[nodiscard]] static int get_day();
    [[nodiscard]] static int get_month();
    [[nodiscard]] static int get_year();
    [[nodiscard]] static int get_days_in_month(int year, int month);
    [[nodiscard]] static int get_consistent_day();
    [[nodiscard]] static int get_yearly_consistent_day();

    // 日付を更新するための関数
    void static date_counter();
};



#endif //TIMER_H
