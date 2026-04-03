#include "sudoku_generator.h"

#include <algorithm>
#include <array>
#include <numeric>
#include <vector>

SudokuGenerator::SudokuGenerator()
    : rng_(std::random_device{}()) {}

GeneratedPuzzle SudokuGenerator::generate(SudokuDifficulty difficulty) {
    SudokuBoard solution;
    fillBoard(solution);

    SudokuBoard puzzle = solution;
    int clues = 81;
    const int target = targetClues(difficulty);

    std::vector<int> positions(81);
    std::iota(positions.begin(), positions.end(), 0);

    for (int pass = 0; pass < 4 && clues > target; ++pass) {
        std::shuffle(positions.begin(), positions.end(), rng_);

        bool changed = false;
        for (int idx : positions) {
            if (clues <= target) {
                break;
            }

            const int row = idx / 9;
            const int col = idx % 9;
            const int backup = puzzle.get(row, col);
            if (backup == 0) {
                continue;
            }

            puzzle.set(row, col, 0);
            if (solver_.countSolutions(puzzle, 2) != 1) {
                puzzle.set(row, col, backup);
                continue;
            }

            --clues;
            changed = true;
        }

        if (!changed) {
            break;
        }
    }

    GeneratedPuzzle generated;
    generated.puzzle = puzzle;
    generated.solution = solution;
    generated.difficulty = difficulty;

    for (int row = 0; row < 9; ++row) {
        for (int col = 0; col < 9; ++col) {
            generated.fixed[row * 9 + col] = puzzle.get(row, col) != 0;
        }
    }

    return generated;
}

std::string SudokuGenerator::difficultyName(SudokuDifficulty difficulty) {
    switch (difficulty) {
    case SudokuDifficulty::Easy:
        return "easy";
    case SudokuDifficulty::Medium:
        return "medium";
    case SudokuDifficulty::Hard:
        return "hard";
    }
    return "unknown";
}

bool SudokuGenerator::fillBoard(SudokuBoard& board) {
    int bestRow = -1;
    int bestCol = -1;
    std::vector<int> bestCandidates;
    int bestSize = 10;

    for (int row = 0; row < 9; ++row) {
        for (int col = 0; col < 9; ++col) {
            if (board.get(row, col) != 0) {
                continue;
            }

            std::vector<int> options = board.candidates(row, col);
            if (options.empty()) {
                return false;
            }
            if (static_cast<int>(options.size()) < bestSize) {
                bestSize = static_cast<int>(options.size());
                bestRow = row;
                bestCol = col;
                bestCandidates = std::move(options);
                if (bestSize == 1) {
                    break;
                }
            }
        }
        if (bestSize == 1) {
            break;
        }
    }

    if (bestRow == -1) {
        return true;
    }

    std::shuffle(bestCandidates.begin(), bestCandidates.end(), rng_);
    for (int value : bestCandidates) {
        board.set(bestRow, bestCol, value);
        if (fillBoard(board)) {
            return true;
        }
        board.set(bestRow, bestCol, 0);
    }

    return false;
}

int SudokuGenerator::targetClues(SudokuDifficulty difficulty) const {
    switch (difficulty) {
    case SudokuDifficulty::Easy:
        return 40;
    case SudokuDifficulty::Medium:
        return 32;
    case SudokuDifficulty::Hard:
        return 26;
    }
    return 32;
}
