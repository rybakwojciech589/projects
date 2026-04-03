#include "sudoku_board.h"
#include "sudoku_generator.h"

#include <algorithm>
#include <cctype>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

namespace {

std::string trim(const std::string& input) {
    std::size_t left = 0;
    std::size_t right = input.size();

    while (left < input.size() && std::isspace(static_cast<unsigned char>(input[left]))) {
        ++left;
    }
    while (right > left && std::isspace(static_cast<unsigned char>(input[right - 1]))) {
        --right;
    }
    return input.substr(left, right - left);
}

std::string toLower(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return value;
}

void printBanner() {
    std::cout
        << "=============================================\n"
        << " Sudoku Lab - generator, solver and game\n"
        << "=============================================\n\n";
}

void printMainMenu() {
    std::cout
        << "1. Play generated puzzle\n"
        << "2. Quit\n\n";
}

void printPlayHelp() {
    std::cout
        << "Commands in play mode:\n"
        << "  set <row> <col> <value>   place a number\n"
        << "  clear <row> <col>         clear a non-fixed cell\n"
        << "  cand <row> <col>          show candidates\n"
        << "  check                     show current status\n"
        << "  hint                      fill one correct cell\n"
        << "  solve                     show the solution and leave play mode\n"
        << "  quit                      leave play mode\n"
        << "  help                      show this help\n\n";
}

std::optional<int> readMenuChoice() {
    std::cout << "Choose an option > ";
    std::string line;
    if (!std::getline(std::cin, line)) {
        return std::nullopt;
    }
    line = trim(line);
    if (line.empty()) {
        return std::nullopt;
    }
    try {
        return std::stoi(line);
    } catch (...) {
        return std::nullopt;
    }
}

std::optional<SudokuDifficulty> promptDifficulty() {
    std::cout
        << "Choose difficulty:\n"
        << "  1. Easy\n"
        << "  2. Medium\n"
        << "  3. Hard\n"
        << "> ";

    std::string line;
    if (!std::getline(std::cin, line)) {
        return std::nullopt;
    }

    line = toLower(trim(line));
    if (line == "1" || line == "easy") {
        return SudokuDifficulty::Easy;
    }
    if (line == "2" || line == "medium") {
        return SudokuDifficulty::Medium;
    }
    if (line == "3" || line == "hard") {
        return SudokuDifficulty::Hard;
    }
    return std::nullopt;
}

bool parseThreeInts(const std::string& line, int& a, int& b, int& c) {
    std::istringstream iss(line);
    std::string command;
    return static_cast<bool>(iss >> command >> a >> b >> c);
}

bool parseTwoInts(const std::string& line, int& a, int& b) {
    std::istringstream iss(line);
    std::string command;
    return static_cast<bool>(iss >> command >> a >> b);
}

void playPuzzle(SudokuGenerator& generator) {
    const auto difficulty = promptDifficulty();
    if (!difficulty.has_value()) {
        std::cout << "Invalid difficulty.\n\n";
        return;
    }

    GeneratedPuzzle generated = generator.generate(*difficulty);
    SudokuBoard current = generated.puzzle;

    std::cout << "\nPuzzle ready. Difficulty: " << SudokuGenerator::difficultyName(*difficulty)
              << " | clues: " << current.clueCount() << "\n\n";
    printPlayHelp();

    while (true) {
        current.print(std::cout, generated.fixed);
        std::cout << "\nplay> ";

        std::string line;
        if (!std::getline(std::cin, line)) {
            std::cout << "\n";
            return;
        }

        line = trim(line);
        if (line.empty()) {
            continue;
        }

        const std::string lower = toLower(line);

        if (lower == "quit") {
            std::cout << "Leaving play mode.\n\n";
            return;
        }
        if (lower == "help") {
            printPlayHelp();
            continue;
        }
        if (lower == "check") {
            std::cout << "Clues filled: " << 81 - current.emptyCount()
                      << "/81 | consistent: " << (current.isConsistent() ? "yes" : "no") << "\n\n";
            if (current.isSolved()) {
                std::cout << "Congratulations, puzzle solved.\n\n";
                return;
            }
            continue;
        }
        if (lower == "solve") {
            std::cout << "Solution:\n";
            generated.solution.print(std::cout);
            std::cout << "\n";
            return;
        }
        if (lower == "hint") {
            bool filled = false;
            for (int row = 0; row < 9 && !filled; ++row) {
                for (int col = 0; col < 9 && !filled; ++col) {
                    if (current.get(row, col) == 0) {
                        current.set(row, col, generated.solution.get(row, col));
                        filled = true;
                    }
                }
            }
            if (!filled) {
                std::cout << "No empty cells left.\n\n";
            } else {
                std::cout << "Filled one correct cell.\n\n";
            }
            continue;
        }
        if (lower.rfind("cand ", 0) == 0) {
            int row = 0;
            int col = 0;
            if (!parseTwoInts(line, row, col) || row < 1 || row > 9 || col < 1 || col > 9) {
                std::cout << "Usage: cand <row> <col>\n\n";
                continue;
            }

            const std::vector<int> candidates = current.candidates(row - 1, col - 1);
            if (current.get(row - 1, col - 1) != 0) {
                std::cout << "That cell is already filled.\n\n";
            } else if (candidates.empty()) {
                std::cout << "No legal candidates for that cell.\n\n";
            } else {
                std::cout << "Candidates:";
                for (int value : candidates) {
                    std::cout << ' ' << value;
                }
                std::cout << "\n\n";
            }
            continue;
        }
        if (lower.rfind("clear ", 0) == 0) {
            int row = 0;
            int col = 0;
            if (!parseTwoInts(line, row, col) || row < 1 || row > 9 || col < 1 || col > 9) {
                std::cout << "Usage: clear <row> <col>\n\n";
                continue;
            }

            const int idx = (row - 1) * 9 + (col - 1);
            if (generated.fixed[idx]) {
                std::cout << "You cannot clear a fixed clue.\n\n";
                continue;
            }
            current.set(row - 1, col - 1, 0);
            std::cout << "Cell cleared.\n\n";
            continue;
        }
        if (lower.rfind("set ", 0) == 0) {
            int row = 0;
            int col = 0;
            int value = 0;
            if (!parseThreeInts(line, row, col, value) || row < 1 || row > 9 || col < 1 || col > 9 || value < 1 || value > 9) {
                std::cout << "Usage: set <row> <col> <value>\n\n";
                continue;
            }

            const int idx = (row - 1) * 9 + (col - 1);
            if (generated.fixed[idx]) {
                std::cout << "You cannot modify a fixed clue.\n\n";
                continue;
            }

            if (!current.isValidPlacement(row - 1, col - 1, value)) {
                std::cout << "That value breaks Sudoku rules.\n\n";
                continue;
            }

            current.set(row - 1, col - 1, value);
            if (current.isSolved()) {
                current.print(std::cout, generated.fixed);
                std::cout << "\nCongratulations, puzzle solved.\n\n";
                return;
            }
            continue;
        }

        std::cout << "Unknown command. Type `help`.\n\n";
    }
}

}

int main() {
    SudokuGenerator generator;

    printBanner();

    while (true) {
        printMainMenu();
        const auto choice = readMenuChoice();
        if (!choice.has_value()) {
            if (!std::cin) {
                std::cout << "\n";
                break;
            }
            std::cout << "Invalid choice.\n\n";
            continue;
        }

        switch (*choice) {
        case 1:
            playPuzzle(generator);
            break;
        case 2:
            std::cout << "Bye.\n";
            return 0;
        default:
            std::cout << "Invalid choice.\n\n";
            break;
        }
    }

    std::cout << "Bye.\n";
    return 0;
}
