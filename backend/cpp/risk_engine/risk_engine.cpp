#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

namespace {

constexpr std::size_t MAX_HAYSTACK_BYTES = 2 * 1024 * 1024;

std::string lower_copy(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    return value;
}

double exposure_multiplier(const std::string& environment) {
    if (environment == "internet") return 1.5;
    if (environment == "production") return 1.25;
    if (environment == "staging") return 1.0;
    return 0.8;
}

double criticality_multiplier(int criticality) {
    switch (criticality) {
        case 1: return 0.7;
        case 2: return 0.9;
        case 3: return 1.0;
        case 4: return 1.25;
        case 5: return 1.5;
        default: return 1.0;
    }
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 2) return 2;
    const std::string mode = argv[1];
    if (mode == "match" && argc == 3) {
        std::ostringstream buffer;
        buffer << std::cin.rdbuf();
        const std::string input = buffer.str();
        if (input.size() > MAX_HAYSTACK_BYTES) return 3;
        const std::string package_name = lower_copy(argv[2]);
        const std::string haystack = lower_copy(input);
        std::cout << (haystack.find(package_name) != std::string::npos ? "1" : "0") << "\n";
        return 0;
    }
    if (mode == "risk" && argc == 5) {
        const double cvss = std::stod(argv[4]);
        const double score = std::min(cvss * criticality_multiplier(std::stoi(argv[3])) * exposure_multiplier(argv[2]), 10.0);
        std::cout << std::fixed << std::setprecision(2) << (std::round(score * 100.0) / 100.0) << "\n";
        return 0;
    }
    return 2;
}
// Project version: VulnScope V1.5

