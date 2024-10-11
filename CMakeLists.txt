cmake_minimum_required(VERSION 3.22)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(BEGenerate)

project("config_gen")

add_subdirectory("src")

