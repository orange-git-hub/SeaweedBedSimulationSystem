/// <summary>
/// Created by 石川澄空 on 25/04/16.
/// このスクリプトは，configファイル(yaml)を読み込み，与えられたkeyに一致するvalueを返すためのものである．
/// </summary>



#include "config_loader.h"
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <yaml-cpp/yaml.h>

config_loader::config_loader(const std::string& yaml_path) {
    try {
        root = YAML::LoadFile(yaml_path);
        std::cout << "[DEBUG] YAML file loaded successfully." << std::endl;

        for (const auto& item : root) {
            std::cout << "[DEBUG] Key: " << item.first.as<std::string>() << std::endl;
        }
    } catch (const YAML::Exception& e) {
        std::cerr << "YAML Error: " << e.what() << std::endl;
        throw;
    }
}


std::vector<std::string> config_loader::split_key(const std::string& key) const {
    std::vector<std::string> result;
    std::stringstream ss(key);
    std::string item;
    while (std::getline(ss, item, '.')) {
        result.push_back(item);
    }
    return result;
}

// 単一のデータをconfigから取得する関数
std::string config_loader::get_value(const std::string &key) const {
    try {
        // ノード取得
        YAML::Node node = root[key];

        // ノードが存在しないか確認
        if (!node.IsDefined()) {
            std::cerr << "[ERROR] Key '" << key << "' is not defined in the YAML file.\n";
            throw std::runtime_error("Key '" + key + "' is not defined.");
        }

        // ノードがスカラーであるか確認
        if (!node.IsScalar()) {
            std::cerr << "[ERROR] Key '" << key << "' is not a scalar value. Type: "
                      << (node.IsMap() ? "Map" : node.IsSequence() ? "Sequence" : "Unknown") << "\n";
            throw std::runtime_error("Key '" + key + "' is not a scalar value.");
        }

        // 正常なスカラー値として返却
        return node.as<std::string>();

    } catch (const YAML::Exception &e) {
        std::cerr << "[ERROR] YAML Exception while fetching key '" << key << "': " << e.what() << "\n";
        throw;
    } catch (const std::exception &e) {
        std::cerr << "[ERROR] Exception while fetching key '" << key << "': " << e.what() << "\n";
        throw;
    }
}


// リスト型のデータをconfigから取得する関数
std::vector<std::string> config_loader::get_list(const std::string& key) const {
    std::vector<std::string> keys = split_key(key);
    YAML::Node current = root;
    for (const auto& k : keys) {
        if (!current[k]) {
            throw std::runtime_error("Key not found: " + key);
        }
        current = current[k];
    }

    if (!current.IsSequence()) {
        throw std::runtime_error("Key is not a sequence: " + key);
    }

    std::vector<std::string> result;
    for (const auto& item : current) {
        result.push_back(item.as<std::string>());
    }

    return result;
}