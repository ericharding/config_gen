#include "example-config.h"

#include <fstream>

int main(int, char **) {
  const char *configFilePath =
      "/home/eric/dev/be/config_gen/config/talon_localhost.json";
  std::ifstream stream(configFilePath, std::ios::in);
  if (stream.bad()) {
    std::cerr << "Config file '" << configFilePath << "' not found.\n";
    throw std::runtime_error("Failed to open config");
  }
  auto doc = nlohmann::json::parse(stream);
  auto value = parse_config(doc);

  std::cout << "success" << std::endl;
  std::cout << std::to_string(value) << std::endl;
  return 0;
}

/*

#include <cstdlib>
#include <iostream>
#include <map>
#include <nlohmann/json.hpp>
#include <string>

using json = nlohmann::json;

// Function to get environment variable value
std::string getEnvVar(const std::string& key) {
    char* val = std::getenv(key.c_str());
    return val == nullptr ? "" : std::string(val);
}

// Function to parse a JSON value with environment variable substitution
template<typename T>
T parseJsonValue(const json& value, const T& defaultValue) {
    if (value.is_string()) {
        std::string strValue = value.get<std::string>();
        if (strValue.length() > 3 && strValue[0] == '$' && strValue[1] == '{' &&
strValue.back() == '}') { std::string envVarName = strValue.substr(2,
strValue.length() - 3); std::string envVarValue = getEnvVar(envVarName);

            if (!envVarValue.empty()) {
                // Try to convert the environment variable value to the target
type try { if constexpr (std::is_same_v<T, int>) { return
std::stoi(envVarValue); } else if constexpr (std::is_same_v<T, double>) { return
std::stod(envVarValue); } else if constexpr (std::is_same_v<T, bool>) { return
(envVarValue == "true" || envVarValue == "1"); } else { return envVarValue;
                    }
                } catch (const std::exception& e) {
                    std::cerr << "Error converting environment variable '" <<
envVarName
                              << "' to required type: " << e.what() <<
std::endl; return defaultValue;
                }
            }
        }
    }

    // If it's not a string or doesn't match the environment variable pattern,
    // try to convert it to the target type
    try {
        return value.get<T>();
    } catch (const json::exception& e) {
        std::cerr << "Error parsing JSON value: " << e.what() << std::endl;
        return defaultValue;
    }
}

std::map<std::string, std::string> parseStringMap(const json& j, const
std::string& key) { std::map<std::string, std::string> resultMap;

    if (!j.contains(key) || !j[key].is_object()) {
        std::cout << "Warning: JSON does not contain an object at key '" << key
<< "'. Returning empty map." << std::endl; return resultMap;
    }

    for (const auto& [mapKey, mapValue] : j[key].items()) {
        resultMap[mapKey] = parseJsonValue<std::string>(mapValue,
"DEFAULT_VALUE");
    }

    return resultMap;
}

int main() {
    // Example JSON string with nested string-to-string map and environment
variable references std::string jsonString = R"(
    {
        "id": "${USER_ID}",
        "name": "Example Object",
        "stringMap": {
            "key1": "value1",
            "key2": "${HOME}",
            "key3": null,
            "key4": 42,
            "key5": "${BOOL_VALUE}"
        },
        "otherProperty": [1, 2, 3]
    })";

    try {
        json j = json::parse(jsonString);

        std::map<std::string, std::string> resultMap = parseStringMap(j,
"stringMap");

        std::cout << "Parsed string map:" << std::endl;
        for (const auto& [key, value] : resultMap) {
            std::cout << key << ": " << value << std::endl;
        }

        std::cout << "\nOther properties:" << std::endl;
        std::cout << "ID: " << parseJsonValue<int>(j["id"], -1) << std::endl;
        std::cout << "Name: " << parseJsonValue<std::string>(j["name"],
"Unknown") << std::endl; std::cout << "Missing Key: " <<
parseJsonValue<std::string>(j["missingKey"], "Not Found") << std::endl;
    }
    catch (json::parse_error& e) {
        std::cerr << "JSON parse error: " << e.what() << std::endl;
    }
    catch (std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}

*/
