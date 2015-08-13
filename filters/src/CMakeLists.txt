cmake_minimum_required(VERSION 2.6)

#{{{ Sources

set(ufofilter_SRCS
    ufo-cut-roi-task.c
    ufo-fftconvolution-task.c
    ufo-hessian-kernel-task.c
    ufo-hessian-analysis-task.c
    ufo-ordfilt-task.c
    ufo-ring-pattern-task.c
    ufo-ring-writer-task.c
    ufo-local-maxima-task.c
    ufo-blob-test-task.c
    ufo-label-cluster-task.c
    ufo-combine-test-task.c
    ufo-sum-task.c
    ufo-log-task.c
    ufo-brightness-cut-task.c
    ufo-contrast-task.c
    )

#}}}
#{{{ Variables

set(ufofilter_LIBS
    ${UFO_LIBRARIES}
    oclfft)

if (CMAKE_COMPILER_IS_GNUCC OR ("${CMAKE_C_COMPILER_ID}" STREQUAL "Clang"))
    add_definitions("-Wcast-align -Wcast-qual -Winline -Wmissing-declarations "
                    "-Wmissing-prototypes -Wnested-externs -Wno-long-long "
                    "-Wno-missing-field-initializers -Wpointer-arith "
                    "-Wredundant-decls -Wshadow -Wstrict-prototypes -Wwrite-strings")
endif()

#}}}
#{{{ Dependency checks

find_package(clFFT)
if (CLFFT_FOUND)
    include_directories(${CLFFT_INCLUDE_DIRS})
    list(APPEND ufofilter_LIBS ${CLFFT_LIBRARIES})
    set(HAVE_AMD ON)
endif ()

set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp")

#}}}
#{{{ Build targets

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/config.h.in
               ${CMAKE_CURRENT_BINARY_DIR}/config.h)

foreach(_src ${ufofilter_SRCS})
    # find plugin suffix
    string(REGEX REPLACE "ufo-([^ \\.]+)-task.*" "\\1" task "${_src}")

    # build string to get miscalleanous sources
    string(REPLACE "-" "_" _misc ${task})
    string(TOUPPER ${_misc} _misc_upper)

    # create an option name and add this to disable filters
    set(target_option "ENABLE_${_misc_upper}")
    option(${target_option} "Build filter ${task}" ON)

    if (${target_option})
        set(_misc "${_misc}_misc_SRCS")

        string(REPLACE "-" "" _targetname ${task})
        set(target "ufofilter${_targetname}")

        # build single shared library per filter
        if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
            add_library(${target} MODULE ${ufoaux_SRCS} ${_src} ${${_misc}})
        else()
            add_library(${target} SHARED ${ufoaux_SRCS} ${_src} ${${_misc}})
        endif()

        target_link_libraries(${target} ${ufofilter_LIBS})

        list(APPEND all_targets ${target})

        install(TARGETS ${target}
                ARCHIVE DESTINATION ${LOCAL_BUILD_DIR}
                LIBRARY DESTINATION ${LOCAL_BUILD_DIR})
    endif()
endforeach()

#}}} 
