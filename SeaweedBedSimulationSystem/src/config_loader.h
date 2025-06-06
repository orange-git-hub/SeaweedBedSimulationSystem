//
// Created by 石川澄空 on 25/04/16.
//

#ifndef CONFIG_LOADER_H
#define CONFIG_LOADER_H

#pragma once

#include <string>
#include <vector>
#include <yaml-cpp/yaml.h>


class config_loader {
    YAML::Node root;

    std::vector<std::string> split_key(const std::string& key) const;

public:
    explicit config_loader(const std::string& yaml_path);

    std::string get_value(const std::string& key) const; // 単一のデータを取得する関数
    std::vector<std::string> get_list(const std::string& key) const;  // listデータを取得する関数
};


#endif //CONFIG_LOADER_H
