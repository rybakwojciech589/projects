# Sudoku Lab

A terminal-based Sudoku game written in **C++20**. The project combines puzzle generation, board validation, and interactive play in a compact command-line application, while using a built-in solving engine behind the scenes to keep generated boards consistent and uniquely solvable.

---

## Features

* **Procedural Puzzle Generation:** Creates new Sudoku boards on demand instead of relying on a static puzzle list.
* **Multiple Difficulty Levels:** Supports Easy, Medium, and Hard generated puzzles.
* **Interactive Terminal Gameplay:** Play directly in the console with a simple command-driven interface.
* **Built-in Solver Engine:** Uses recursive backtracking internally to solve boards and verify puzzle correctness.
* **Hint and Candidate Tools:** Includes in-game commands for candidate checking, board validation, and filling one correct cell.
* **Unique-Solution Checks:** Generated puzzles are validated so they remain proper Sudoku instances instead of random incomplete grids.
* **Modular C++ Project Structure:** Board logic, solver logic, generator logic, and CLI flow are separated into clear files.
* **CMake Build System:** Easy to compile on Linux, macOS, WSL, and Windows toolchains that support CMake and C++20.

---

## Installation & Setup

**1. Prerequisites**
* A C++20-compatible compiler.
* [CMake](https://cmake.org/) installed on your system.

**2. Clone the repository**
```bash
git clone https://github.com/rybakwojciech589/projects.git
cd projects/sudoku
```

**3. Build the project**
```bash
cmake -S . -B build
cmake --build build
```

**4. Run the game**
```bash
./build/sudoku_lab
```

On some Windows setups, the executable may appear inside a configuration subfolder such as `build/Debug` or `build/Release`.

---

## How to Play

Start the program, choose `Play generated puzzle`, pick a difficulty level, and solve the board directly in the terminal.

The goal is standard Sudoku:

* Every row must contain the digits `1-9` exactly once.
* Every column must contain the digits `1-9` exactly once.
* Every `3x3` subgrid must contain the digits `1-9` exactly once.

**In-Game Commands:**
* `set <row> <col> <value>` � Place a number in a cell.
* `clear <row> <col>` � Clear a non-fixed cell.
* `cand <row> <col>` � Show legal candidates for a cell.
* `check` � Display the current board status.
* `hint` � Fill one correct cell.
* `solve` � Show the full solution and exit play mode.
* `help` � Show the command list.
* `quit` � Leave play mode.

---

## How it works under the hood

The project is built from a few focused components:

* **`SudokuBoard`** stores the 9x9 grid and handles validation, consistency checks, clue counting, and candidate generation.
* **`SudokuSolver`** uses recursive backtracking to solve incomplete boards and support validation during generation.
* **`SudokuGenerator`** starts from a valid completed grid and removes clues while preserving puzzle quality.
* **`main.cpp`** provides the terminal interface, difficulty selection, and play loop.

The key idea is that puzzle generation is not just random cell removal. The generator relies on solver-backed checks so the resulting board is still playable as an actual Sudoku puzzle, not just an arbitrary broken state.

---

This project is a compact showcase of core C++ topics applied to a classic logic game: recursion, state management, validation, modular multi-file design, and terminal-based interaction.

