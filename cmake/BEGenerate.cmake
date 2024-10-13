cmake_minimum_required(VERSION 3.22)

# A low level generate macro that can be used to build tool specific generate macros
# NOTE: tool must be an absolute path with no spaces. i.e. use an executable script rather than python foo.py
function(BE_GENERATE INPUT_FILE OUTPUT_DIR TOOL)
    cmake_parse_arguments(ARG "" "LIBNAME" "ENV" ${ARGN})
    get_filename_component(FILE_NAME ${INPUT_FILE} NAME)
    get_filename_component(NAME_WITHOUT_EXT "${FILE_NAME}" NAME_WE)
    set(TARGET_NAME BE_GENERATE_TARGET_${FILE_NAME})
    set(TARGET_DIR ${OUTPUT_DIR}/${NAME_WITHOUT_EXT}/${NAME_WITHOUT_EXT})
    set(DEFAULT_LIBRARY_NAME "lib-${NAME_WITHOUT_EXT}")
    set(LIBRARY_NAME ${ARG_LIBNAME})
    if(NOT LIBRARY_NAME)
        set(LIBRARY_NAME ${DEFAULT_LIBRARY_NAME})
    endif()

    file(MAKE_DIRECTORY ${TARGET_DIR})

    set(ENV_COMMNAD)
    if (ARG_ENV)
        set(ENV_COMMAND ${CMAKE_COMMAND} -E env ${ARG_ENV})
    endif()
    message(STATUS "${FILE_NAME} ENV_COMMAND=${ENV_COMMAND}")

    # Add a custom command to run the tool and generate headers
    # Also create a predictable dummy file we can use to determine if we need to re-run
    add_custom_command(
        OUTPUT ${TARGET_DIR}/dummy
        COMMAND ${ENV_COMMAND} ${TOOL} ${INPUT_FILE} ${TARGET_DIR}
        COMMAND ${CMAKE_COMMAND} -E touch ${TARGET_DIR}/dummy
        DEPENDS ${INPUT_FILE} ${TOOL} 
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Generating headers from ${INPUT_FILE} into ${TARGET_DIR}"
    )

    # Add a custom target to ensure the headers are generated
    add_custom_target(${TARGET_NAME}
        DEPENDS ${TARGET_DIR}/dummy
    )

    # Create an INTERFACE library
    add_library(${LIBRARY_NAME} INTERFACE)

    # Add the generated headers directory to the INTERFACE library's include directories
    set(INCLUDE_DIR "${TARGET_DIR}/..")
    cmake_path(NORMAL_PATH INCLUDE_DIR)
    target_include_directories(${LIBRARY_NAME} INTERFACE ${INCLUDE_DIR})
    message(STATUS "Include path for ${LIBRARY_NAME} is ${INCLUDE_DIR}")

    # Ensure the headers are generated before building the INTERFACE library
    add_dependencies(${LIBRARY_NAME} ${TARGET_NAME})
    
    message(STATUS "Added library ${LIBRARY_NAME} depending on generated output from ${FILE_NAME}")
    set(LIBRARY_NAME ${LIBRARY_NAME} PARENT_SCOPE)
endfunction()

# To use GE_GENERATE wrap it in a function to run the specific generation tool
function(CONFIG_GENERATE INPUT_FILE)
    BE_GENERATE(
        ${INPUT_FILE} 
        ${CMAKE_BINARY_DIR}/_gen_config 
        "${CMAKE_SOURCE_DIR}/script/config_gen.py"
        )
    target_link_libraries(${LIBRARY_NAME} INTERFACE nlohmann_json::nlohmann_json)
endfunction()

