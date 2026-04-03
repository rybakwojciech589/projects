cmake_minimum_required(VERSION 3.16)

project(SudokuLab LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(sudoku_lab
    src/main.cpp
    src/sudoku_board.cpp
    src/sudoku_generator.cpp
    src/sudoku_solver.cpp
)

target_include_directories(sudoku_lab PRIVATE include)

if(MSVC)
    target_compile_options(sudoku_lab PRIVATE /W4 /permissive- /utf-8)
else()
    target_compile_options(sudoku_lab PRIVATE -Wall -Wextra -Wpedantic)
endif()
