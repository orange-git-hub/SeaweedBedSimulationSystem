/// <summary>
/// Created by 石川澄空 on 25/04/22.
/// </summary>

#pragma once



# include "animal.h"

class fish : public animal
{
private:
	int id;
	double delta_increase_body_weight;

public:
	explicit fish(int id_argument);
	// animal クラスから継承した純粋仮想関数のオーバーライド
	double body_weight_increase_calculator(double water_temperature) override;
	double feed_amount_calculator() override;
	double aging_effect(int day_age) override;
	double temperature_effect(double water_temperature) override;
};




