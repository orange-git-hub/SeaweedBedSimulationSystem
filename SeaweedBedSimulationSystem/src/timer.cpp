/// <summary>
/// Created by 石川澄空 on 25/04/16.
/// このスクリプトはsimulationのステップ管理，simulation内時間管理を行うものである．
/// </summary>

#include "timer.h"
#include <iostream>
#include "config_loader.h"
#include <stdexcept>

// staticなメンバ変数の定義．
int timer::day = 1;
int timer::month = 1;
int timer::year = 1;
int timer::days_in_month = 30;
int timer::consistent_day = 1;
int timer::yearly_consistent_day = 0;

// コンストラクタ定義
timer::timer(const std::string& config_path) {
    config_loader config(config_path);

    try {
        std::cout << "[DEBUG] Loading configuration: simulation_day_range" << std::endl;
        int test_value = std::stoi(config.get_value("simulation_day_range"));
        std::cout << "[DEBUG] simulation_day_range: " << test_value << std::endl;

        std::cout << "[DEBUG] Loading initial_date values" << std::endl;

        // individual key access with debugging
        year = std::stoi(config.get_value("initial_year"));
        std::cout << "[DEBUG] initial_year value: " << year << std::endl;

        month = std::stoi(config.get_value("initial_month"));
        std::cout << "[DEBUG] initial_month value: " << month << std::endl;

        day = std::stoi(config.get_value("initial_day"));
        std::cout << "[DEBUG] initial_day value: " << day << std::endl;

        std::cout << "[DEBUG] Initial date: " << year << "-" << month << "-" << day << std::endl;

        consistent_day = 1;
        decide_days_in_month(year, month);
    } catch (const std::runtime_error& e) {
        std::cerr << "Error loading configuration: " << e.what() << std::endl;
        year = 1;
        month = 1;
        day = 1;
        days_in_month = 30;

    }
    std::cout << "timer end" << std::endl;
}



// 閏年かどうかを判断
bool timer::check_is_leap_year(int check_year)
{
    return (check_year % 4 == 0 && check_year % 100 != 0) || check_year % 400 == 0;
}

// その月の長さを決定
void timer::decide_days_in_month(int check_year, int check_month)
{
    int natural_days_in_month_array[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };

    if (check_month == 2 && check_is_leap_year(check_year))
    {
        days_in_month = 29;
    }
    days_in_month = natural_days_in_month_array[check_month - 1];
}

// ゲッター関数定義
int timer::get_day() { return day; }
int timer::get_month() { return month; }
int timer::get_year() { return year; }
int timer::get_consistent_day() { return consistent_day; }
int timer::get_yearly_consistent_day() { return yearly_consistent_day; }
int timer::get_days_in_month(int year, int month)
{
    decide_days_in_month(year, month);
    return days_in_month;
}

// 日付を進める関数定義
void timer::date_counter() {
    day++;
    consistent_day++;
    yearly_consistent_day++;
    if (day > get_days_in_month(year,month)) {
        day = 1;
        month++;
        if (month > 12) {
            month = 1;
            year++;
            yearly_consistent_day = 0;
        }
        decide_days_in_month(year, month);
    }
}