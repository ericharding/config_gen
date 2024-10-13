import xml.etree.ElementTree as ET
import sys

def parse_xml_schema(xml_string):
    root = ET.fromstring(xml_string)
    types = {}
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        type_kind = type_elem.get('type')
        if type_kind == 'enum':
            types[name] = {'kind': 'enum', 'values': {}}
            for value_elem in type_elem.findall('value'):
                types[name]['values'][value_elem.get('name')] = int(value_elem.text)
        elif type_kind == 'struct':
            types[name] = {'kind': 'struct', 'fields': []}
            for field_elem in type_elem.findall('field'):
                default_value = field_elem.get('default', '')
                types[name]['fields'].append({
                    'name': field_elem.get('name'),
                    'type': field_elem.get('type'),
                    'default': field_elem.get('default', ''),
                    'presence' : field_elem.get('presence', default_value == '' and 'required' or 'optional')
                })
    return types

def generate_includes():
    return "\n".join([
        "#pragma once\n",
        "#include <map>",
        "#include <optional>",
        "#include <ostream>",
        "#include <set>",
        "#include <string>",
        "#include <vector>",
        "#include <nlohmann/json.hpp>",
        "\n\n"
        ])

def generate_cpp_types(types):
    cpp_code = generate_includes()
    
    for name, type_info in types.items():
        if type_info['kind'] == 'enum':
            cpp_code += f"enum class {name} {{\n"
            for enum_name, enum_value in type_info['values'].items():
                cpp_code += f"    {enum_name} = {enum_value},\n"
            cpp_code += "};\n\n"
        elif type_info['kind'] == 'struct':
            cpp_code += f"struct {name} {{\n"
            for field in type_info['fields']:
                cpp_type = get_cpp_type(field['type'])
                cpp_code += f"    {cpp_type} {field['name']};\n"
            cpp_code += "};\n\n"
    
    return cpp_code

ARRAY_PREFIX = "array["
MAP_PREFIX = "map["

def is_primitive(xml_type):
    return xml_type in ['int', 'uint', 'string', 'double']

def get_cpp_type(xml_type):
    if xml_type == 'string':
        return 'std::string'
    elif xml_type == 'uint':
        return 'uint32_t'
    elif xml_type == 'int':
        return 'int32_t'
    elif xml_type.startswith(ARRAY_PREFIX):
        inner_type = xml_type[len(ARRAY_PREFIX):-1]
        return f'std::vector<{get_cpp_type(inner_type)}>'
    elif xml_type.startswith(MAP_PREFIX):
        inner_type = xml_type[len(MAP_PREFIX):-1]
        return f'std::map<std::string,{get_cpp_type(inner_type)}>'
    else:
        return xml_type

def generate_json_parser_fwd(types):
    parser_code = "\n// JSON parsing declarations\n"
    for name, type_info in types.items():
        parser_code += f"inline {name} parse_{name.lower()}(const nlohmann::json&);\n"
    return parser_code

def is_string(field):
    return field['type'] == 'string'

def is_array(field):
    return field['type'].startswith(ARRAY_PREFIX)

def is_map(field):
    return field['type'].startswith(MAP_PREFIX)

def generate_printers(types):
    parser_code = "\n// Print generated types\n"
    parser_code += "namespace std {\n"
    parser_code += "template <class T>"
    parser_code += "std::string to_string(const T& t, uint indent_spaces) {\n"
    parser_code += "  std::string indent(indent_spaces, ' ');\n"
    parser_code += "  return indent+std::to_string(t);\n"
    parser_code += "}\n"
    for name, type_info in types.items():
        parser_code += f"inline std::string to_string(const {name}& value, uint indent_spaces=0) {{\n"
        parser_code += "    std::string indent(indent_spaces, ' ');\n"
        if type_info['kind'] == 'enum':
            parser_code += "    switch(value) {\n"
            for value in type_info['values']:
                parser_code += f"        case {name}::{value}: return \"{value}\"; \n"
            parser_code += f"        default: return \"\"; \n"
            parser_code += "    }\n"
        elif type_info['kind'] == 'struct':
            parser_code += f"    std::string result = \"{name} {{\\n\";\n"
            for field in type_info['fields']:
                if is_string(field):
                    parser_code += f"    result += indent+\"  {field['name']} = '\" + value.{field['name']} + \"'\\n\";\n"
                elif is_array(field):
                    inner_type = field['type'][len(ARRAY_PREFIX):-1]
                    parser_code += f"    result += indent+\"  {field['name']} [\\n\";\n"
                    parser_code += f"    for (auto& i : value.{field['name']}) {{\n"
                    if inner_type == 'string':
                        parser_code += f"        result += indent+\"    '\" + i + \"'\\n\";\n"
                    elif is_primitive(inner_type):
                        parser_code += f"        result += indent+\"    \" + to_string(i) + \"\\n\";\n"
                    else:
                        parser_code += f"        result += indent+\"    \" + to_string(i,indent_spaces+4) + \"\\n\";\n"
                    parser_code += f"    }};\n"
                    parser_code += f"    result += indent+\"  ]\\n\";\n"
                elif is_map(field):
                    inner_type = field['type'][len(MAP_PREFIX):-1]
                    parser_code += f"    result += indent+\"  {field['name']} {{\\n\";\n"
                    parser_code += f"    for (const auto& [key, value] : value.{field['name']}) {{\n"
                    if inner_type == 'string':
                        parser_code += f"        result += indent+\"    '\" + key + \"': '\" + value + \"'\\n\";\n"
                    elif is_primitive(inner_type):
                        parser_code += f"        result += indent+\"    '\" + key + \"': \" + to_string(value) + \"\\n\";\n"
                    else:
                        parser_code += f"        result += indent+\"    '\" + key + \"': \" + to_string(value, indent_spaces+4) + \"\\n\";\n"
                    parser_code += f"    }}\n"
                    parser_code += f"    result += indent+\"  }}\\n\";\n"
                elif not is_primitive(field['type']):
                    parser_code += f"    result += indent+\"  {field['name']} = \" + to_string(value.{field['name']}, indent_spaces+2) + \"\\n\";\n"
                else:
                    parser_code += f"    result += indent+\"  {field['name']} = \" + to_string(value.{field['name']}) + \"\\n\";\n"
            parser_code += f"    result += indent+\"}}\\n\";\n"
            parser_code += f"    return result;\n"
        parser_code += "}\n"
    parser_code += "} // namespace std\n\n"
    for name, type_info in types.items():
        parser_code += f"inline std::ostream& operator<<(std::ostream& out, const {name}& value) {{\n"
        parser_code += "    out << std::to_string(value);\n" 
        parser_code += "    return out;\n"
        parser_code += "}\n"
    return parser_code

def get_default_value(field):
    if field['default'] == '':
        return "std::nullopt"
    if field['type'] == 'string':
        return f"\"{field['default']}\""
    else:
        return field['default']

def generate_json_parsers(types):
    parser_code = "\n// JSON parsing functions\n"
    parser_code += "class ParseException : public std::runtime_error {\n"
    parser_code += "public:\n"
    parser_code += "    ParseException(const std::string& message) : std::runtime_error(message) {}\n"
    parser_code += "};\n\n"

    for name, type_info in types.items():
        if type_info['kind'] == 'enum':
            parser_code += f"inline {name} parse_{name.lower()}(const nlohmann::json& j) {{\n"
            parser_code   += "    std::string value = j.get<std::string>();\n"
            for value in type_info['values']:
                parser_code += f"    if (value == \"{value}\") return {name}::{value}; \n"
            parser_code += f"    throw ParseException(\"Invalid enum value \" + value + \" in {name}\");\n"
            parser_code += "}\n\n"
        elif type_info['kind'] == 'struct':
            parser_code += f"inline {name} parse_{name.lower()}(const nlohmann::json& j) {{\n"
            parser_code += f"    {name} result;\n"
            parser_code += "    std::set<std::string> json_fields;\n"
            parser_code += "    for (const auto& item : j.items()) {\n"
            parser_code += "        json_fields.insert(item.key());\n"
            parser_code += "    }\n\n"
            for field in type_info['fields']:
                parser_code += f"    if (j.contains(\"{field['name']}\")) {{\n"
                if is_primitive(field['type']):
                    parser_code += f"        result.{field['name']} = parseJsonValue<{get_cpp_type(field['type'])}>(j.at(\"{field['name']}\"), {get_default_value(field)});\n"
                elif is_array(field):
                    inner_type = field['type'][len(ARRAY_PREFIX):-1]
                    parser_code += f"        for (const auto& item : j.at(\"{field['name']}\")) {{\n"
                    if is_primitive(inner_type):
                        parser_code += f"            result.{field['name']}.push_back(item.get<{get_cpp_type(inner_type)}>());\n"
                    else:
                        parser_code += f"            result.{field['name']}.push_back(parse_{inner_type.lower()}(item));\n"
                    parser_code += "        }\n"
                elif is_map(field):
                    inner_type = field['type'][len(MAP_PREFIX):-1]
                    parser_code += f"        for (const auto& [key,value] : j.at(\"{field['name']}\").items()) {{\n"
                    if is_primitive(inner_type):
                        parser_code += f"            result.{field['name']}[key] = value.get<{get_cpp_type(inner_type)}>();\n"
                    else:
                        parser_code += f"            result.{field['name']}[key] = parse_{inner_type.lower()}(value);\n"
                    parser_code += "        }\n"
                else:
                    parser_code += f"        result.{field['name']} = parse_{field['type'].lower()}(j.at(\"{field['name']}\"));\n"
                parser_code += f"        json_fields.erase(\"{field['name']}\");\n"
                if field['presence'] == 'required':
                    parser_code += "    } else {\n"
                    parser_code += f"      throw ParseException(\"Missing required field '{field['name']}' in {name}\");\n"
                    parser_code += "    }\n\n"
                else:
                    parser_code += "    }\n\n"
            parser_code += "    if (!json_fields.empty()) {\n"
            parser_code += f"        throw ParseException(\"Unexpected field '\" + *json_fields.begin() + \"' in {name}\");\n"
            parser_code += "    }\n"
            parser_code += "    return result;\n"
            parser_code += "}\n\n"
    
    return parser_code

def main(xml_file_path, output_file_path):
    with open(xml_file_path, 'r') as xml_file:
        xml_content = xml_file.read()
    
    types = parse_xml_schema(xml_content)
    cpp_types = generate_cpp_types(types)
    printers = generate_printers(types)
    json_fwd = generate_json_parser_fwd(types);
    json_parsers = generate_json_parsers(types)
    
    with open(output_file_path, 'w') as output_file:
        output_file.write(cpp_types)
        output_file.write(printers)
        output_file.write(json_fwd)
        output_file.write(json_parsers)
    import datetime
    print(f"\n[{datetime.datetime.now()}] Generated {output_file_path} from {xml_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3 or "--help" in sys.argv:
        print("Usage: python script.py <input_xml_file> <output_cpp_file>")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2])
