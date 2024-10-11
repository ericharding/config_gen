cmake_minimum_required(VERSION 3.22)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(CPM)
include(BEGenerate)

CPMAddPackage("gh:nlohmann/json@3.10.5")

project("config_gen")

add_subdirectory("src")

