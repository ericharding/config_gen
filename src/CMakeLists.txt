cmake_minimum_required(VERSION 3.22)

add_executable(config_load main.cpp)
target_include_directories(config_load PRIVATE ../include)
target_link_libraries(config_load PRIVATE nlohmann_json::nlohmann_json)

# SBE_GENERATE("data/example-sbe.xml" "roost.generated")
