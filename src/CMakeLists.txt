cmake_minimum_required(VERSION 3.22)

CONFIG_GENERATE("example-config.xml" "example")

add_executable(config_load main.cpp)
target_include_directories(config_load PRIVATE ../include)
target_link_libraries(config_load PRIVATE lib-example-config)


