#pragma once

#include "sudoku_board.h"
#include "sudoku_solver.h"

#include <array>
#include <random>
#include <string>

enum class SudokuDifficulty {
    Easy,
    Medium,
    Hard
};

struct GeneratedPuzzle {
    SudokuBoard puzzle;
    SudokuBoard solution;
    std::array<bool, 81> fixed{};
    SudokuDifficulty difficulty = SudokuDifficulty::Easy;
};

class SudokuGenerator {
public:
    SudokuGenerator();

    GeneratedPuzzle generate(SudokuDifficulty difficulty);

    static std::string difficultyName(SudokuDifficulty difficulty);

private:
    SudokuSolver solver_;
    std::mt19937 rng_;

    bool fillBoard(SudokuBoard& board);
    int targetClues(SudokuDifficulty difficulty) const;
};
