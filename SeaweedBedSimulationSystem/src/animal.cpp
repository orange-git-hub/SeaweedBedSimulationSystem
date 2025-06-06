/// <summary>
/// Created by 石川澄空 on 25/04/17.
/// 今後開発予定のウニを管理するクラス,fishクラスに継承されるクラス
/// </summary>

#include "animal.h"
#include "config_loader.h"
#include <iostream>
#include <stdexcept>

// コンストラクタ定義
animal::animal(const std::string& config_path)
{
	// コンフィグデータ取得
	try {
		config_loader config(config_path);

		std::cout << "[DEBUG] Attempting to load animal attributes...\n";

		// body_weight 読み込み
		std::cout << "[DEBUG] Loading key: initial_body_weight\n";
		auto node_body_weight = config.get_value("initial_body_weight");
		std::cout << "[DEBUG] Fetched node for 'initial_body_weight': " << node_body_weight << std::endl;

		try {
			body_weight = std::stod(node_body_weight);
		} catch (const std::invalid_argument&) {
			throw std::runtime_error("Invalid format for 'initial_body_weight': " + node_body_weight);
		}
		std::cout << "[DEBUG] Loaded body_weight: " << body_weight << "\n";

		// body_length 読み込み
		std::cout << "[DEBUG] Loading key: initial_body_length\n";
		auto node_body_length = config.get_value("initial_body_length");
		std::cout << "[DEBUG] Fetched node for 'initial_body_length': " << node_body_length << std::endl;

		try {
			body_length = std::stod(node_body_length);
		} catch (const std::invalid_argument&) {
			throw std::runtime_error("Invalid format for 'initial_body_length': " + node_body_length);
		}
		std::cout << "[DEBUG] Loaded body_length: " << body_length << "\n";

		// feed_value 読み込み
		std::cout << "[DEBUG] Loading key: feed_value\n";
		auto node_feed_value = config.get_value("feed_value");
		std::cout << "[DEBUG] Fetched node for 'feed_value': " << node_feed_value << std::endl;

		try {
			feed_value = std::stod(node_feed_value);
		} catch (const std::invalid_argument&) {
			throw std::runtime_error("Invalid format for 'feed_value': " + node_feed_value);
		}
		std::cout << "[DEBUG] Loaded feed_value: " << feed_value << "\n";

	} catch (const std::exception& e) {
		std::cerr << "[ERROR] Failed to initialize animal: " << e.what() << std::endl;
		throw;
	}
}


// feed_amountを返す関数．
double animal::get_feed_amount() const
{
	return feed_amount;
}

// body_weightを返す関数．
double animal::get_body_weight() const
{
	return body_weight;
}
