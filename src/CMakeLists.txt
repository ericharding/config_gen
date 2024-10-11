cmake_minimum_required(VERSION 3.22)

add_executable(config_load main.cpp)
target_include_directories(config_load PRIVATE ../include)

# SBE_GENERATE("data/example-sbe.xml" "roost.generated")
