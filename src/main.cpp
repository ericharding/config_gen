#include "example-config.h"

#include <iostream>
#include <fstream>

int main(int, char**) {
  const char* configFilePath = "/home/eric/dev/be/config_gen/config/talon_localhost.json";
  std::ifstream stream(configFilePath, std::ios::in);
  if (stream.bad()) {
    std::cerr << "Config file '" << configFilePath << "' not found.\n";
    throw std::runtime_error("Failed to open config");
  }
  auto doc = nlohmann::json::parse(stream);
  auto value = parse_config(doc);

  std::cout << "success" << std::endl;
  std::cout << value.gateway.ip << ":" << value.gateway.port << std::endl;
  std::cout << "username: " << value.gateway.username << std::endl;
  return 0;
}
