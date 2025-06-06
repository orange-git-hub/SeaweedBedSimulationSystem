cmake_minimum_required(VERSION 3.21)
project(SeaweedBedSimulationSystem)

# C++のバージョンを設定
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ソースファイルの場所 (CMakeLists.txtからの相対パス)
# CMakeLists.txt と同じ階層にディレクトリがあると仮定
set(PROJECT_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR})
# 設定ファイル用ヘッダの場所 (プロジェクトルート直下の config ディレクトリを仮定)
set(PROJECT_CONFIG_DIR ${CMAKE_CURRENT_SOURCE_DIR}/config)


# Homebrewのパスを追加 (Apple Silicon Macを想定)
list(APPEND CMAKE_PREFIX_PATH "/opt/homebrew")

# YAML-CPP を探す
find_package(yaml-cpp REQUIRED)

# --- ここからデバッグメッセージ ---
message(STATUS "Attempting to find yaml-cpp.")
if(TARGET yaml-cpp::yaml-cpp)
message(STATUS "Target yaml-cpp::yaml-cpp EXISTS.")
get_target_property(YAML_CPP_INCLUDES yaml-cpp::yaml-cpp INTERFACE_INCLUDE_DIRECTORIES)
message(STATUS "yaml-cpp::yaml-cpp INTERFACE_INCLUDE_DIRECTORIES: ${YAML_CPP_INCLUDES}")
if(NOT YAML_CPP_INCLUDES)
message(WARNING "yaml-cpp::yaml-cpp INTERFACE_INCLUDE_DIRECTORIES is EMPTY. Check yaml-cpp installation and its CMake configuration files (e.g., /opt/homebrew/lib/cmake/yaml-cpp/yaml-cpp-config.cmake).")
endif()
else()
message(WARNING "Target yaml-cpp::yaml-cpp DOES NOT EXIST. find_package might have failed to create the imported target correctly.")
# Fallback to check older variables if the target doesn't exist
message(STATUS "Checking for older variables as a fallback:")
message(STATUS "YAML_CPP_INCLUDE_DIRS (legacy from find_package(YAML) or old yaml-cpp): ${YAML_CPP_INCLUDE_DIRS}")
message(STATUS "yaml-cpp_INCLUDE_DIRS (legacy from find_package(yaml-cpp)): ${yaml-cpp_INCLUDE_DIRS}") # Some packages use this form
endif()
# --- ここまでデバッグメッセージ ---


# config_loader ライブラリ
add_library(config_loader
${PROJECT_SOURCE_DIR}/config_loader.cpp
# ${PROJECT_SOURCE_DIR}/config_loader.h # ヘッダは通常add_libraryには不要だが、IDEによっては追加すると認識しやすくなる
)

target_include_directories(config_loader
PUBLIC
${PROJECT_SOURCE_DIR}    # config_loader.h がこのディレクトリにあると仮定
${PROJECT_CONFIG_DIR}    # ./config ディレクトリのヘッダも公開する場合
# yaml-cpp のヘッダは target_link_libraries で yaml-cpp::yaml-cpp を PUBLIC でリンクすれば自動的に伝播する
)

# config_loader が yaml-cpp を使うのでリンク
target_link_libraries(config_loader
PUBLIC
yaml-cpp::yaml-cpp # find_package が提供するインポートターゲット
)


# メイン実行ファイル
add_executable(SeaweedBedSimulationSystem
${PROJECT_SOURCE_DIR}/main.cpp
${PROJECT_SOURCE_DIR}/timer.cpp
${PROJECT_SOURCE_DIR}/living_thing.cpp
${PROJECT_SOURCE_DIR}/animal.cpp
${PROJECT_SOURCE_DIR}/fish.cpp
${PROJECT_SOURCE_DIR}/algae.cpp
${PROJECT_SOURCE_DIR}/daily_temperature_generator.cpp
${PROJECT_SOURCE_DIR}/daily_photosynthesis_rate_generator.cpp
# ${PROJECT_SOURCE_DIR}/daily_photosynthesis_rate_generator.h # ヘッダファイルは add_executable には通常不要
)

# メイン実行ファイルが config_loader ライブラリを使用
# config_loader が yaml-cpp::yaml-cpp を PUBLIC でリンクしているので、
# yaml-cpp のインクルードパスやリンク情報は SeaweedBedSimulationSystem にも伝播するはず
target_link_libraries(SeaweedBedSimulationSystem
PRIVATE
config_loader      # 作成した config_loader ライブラリをリンク
)

# main.cpp などが直接 config_loader.h 以外のヘッダを ${PROJECT_SOURCE_DIR} からインクルードする場合や、
# config_loader からの PUBLIC な include ディレクトリの伝播がうまくいかない場合のために明示的に追加することも検討
target_include_directories(SeaweedBedSimulationSystem
PRIVATE
${PROJECT_SOURCE_DIR} # main.cppが同じsrc内のヘッダ(config_loader.h等)を見つけるため
)
