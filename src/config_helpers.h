#include <iostream>
#include <nlohmann/json.hpp>
#include <optional>

namespace config {

using json = nlohmann::json;

std::string getEnvVar(const std::string &key) {
  char *val = std::getenv(key.c_str());
  if (val == nullptr) {
    throw std::invalid_argument("Environment variable '" + key +
                                "' not present in environment");
  }
  return std::string(val);
}

// Function to parse a JSON value with environment variable substitution
template <typename T>
T parseJsonValue(const json &value, const std::optional<T> &defaultValue) {
  if (value.is_string()) {
    std::string strValue = value.get<std::string>();
    if (strValue.length() > 3 && strValue[0] == '$' && strValue[1] == '{' &&
        strValue.back() == '}') {
      std::string envVarName = strValue.substr(2, strValue.length() - 3);
      std::string envVarValue = getEnvVar(envVarName);

      if (!envVarValue.empty()) {
        // Try to convert the environment variable value to the target type
        try {
          if constexpr (std::is_same_v<T, int32_t> ||
                        std::is_same_v<T, uint32_t>) {
            return std::stoi(envVarValue);
          } else if constexpr (std::is_same_v<T, double>) {
            return std::stod(envVarValue);
          } else if constexpr (std::is_same_v<T, bool>) {
            return (envVarValue == "true" || envVarValue == "1");
          } else {
            return envVarValue;
          }
        } catch (const std::exception &e) {
          std::cerr << "Error converting environment variable '" << envVarName
                    << "' to required type: " << e.what() << std::endl;
          if (defaultValue) {
            return *defaultValue;
          }
        }
      }
    }
  }
  // If it's not a string or doesn't match the environment variable pattern,
  // try to convert it to the target type
  try {
    return value.get<T>();
  } catch (const json::exception &e) {
    std::cerr << "Error parsing JSON value: " << e.what() << std::endl;
    if (defaultValue) {
      return *defaultValue;
    } else {
      throw;
    }
  }
}
} // namespace config
