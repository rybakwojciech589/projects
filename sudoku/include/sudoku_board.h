#pragma once

#include <array>
#include <iosfwd>
#include <optional>
#include <string>
#include <vector>

class SudokuBoard {
public:
    SudokuBoard();

    static std::optional<SudokuBoard> fromString(const std::string& raw);

    int get(int row, int col) const;
    void set(int row, int col, int value);

    bool isValidPlacement(int row, int col, int value) const;
    bool isConsistent() const;
    bool isSolved() const;

    int emptyCount() const;
    int clueCount() const;
    std::vector<int> candidates(int row, int col) const;

    std::string toString() const;
    void print(std::ostream& out, const std::optional<std::array<bool, 81>>& fixed = std::nullopt) const;

private:
    std::array<int, 81> cells_;

    static int index(int row, int col);
};
