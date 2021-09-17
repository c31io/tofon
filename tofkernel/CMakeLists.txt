cmake_minimum_required(VERSION 3.4...3.18)
project(tofkernel)

include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG        v2.7.1
)

FetchContent_GetProperties(pybind11)
if(NOT pybind11_POPULATED)
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
endif()

#add_subdirectory(pybind11)
pybind11_add_module(tofkernel src/main.cpp)

target_compile_definitions(tofkernel PRIVATE VERSION_INFO=${0.1})
