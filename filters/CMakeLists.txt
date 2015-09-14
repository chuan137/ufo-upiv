cmake_minimum_required(VERSION 2.6)
project(UPIV C)

set(PKG_UFO_CORE_MIN_REQUIRED "0.6")
set(LOCAL_BUILD_DIR "${CMAKE_CURRENT_SOURCE_DIR}/.build")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

find_package(OpenCL REQUIRED)
find_package(PkgConfig REQUIRED)
find_package(GSL REQUIRED)
find_package(OCLFFT)

#{{{ Dependencies

pkg_check_modules(UFO ufo>=${PKG_UFO_CORE_MIN_REQUIRED} REQUIRED)
#MESSAGE(${UFO_KERNELDIR})
#MESSAGE(${UFO_LIBRARY_DIRS})
link_directories(${UFO_LIBRARY_DIRS})
include_directories(${UFO_INCLUDE_DIRS}
                    ${OPENCL_INCLUDE_DIRS}
                    ${CMAKE_CURRENT_SOURCE_DIR}/include)

#}}}
#{{{ Global definitions

add_definitions("-std=c99 -pedantic -Wall -Wextra -fPIC")
add_definitions(-DG_LOG_DOMAIN="Ufo")
if (CMAKE_COMPILER_IS_GNUCC OR ("${CMAKE_C_COMPILER_ID}" STREQUAL "Clang"))
    add_definitions("-Wno-unused-parameter")
endif ()

#}}}
#{{{ Subdirectories

add_subdirectory(src)

#}}}
