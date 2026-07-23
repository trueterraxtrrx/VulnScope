#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace {

constexpr std::size_t MAX_HAYSTACK_BYTES = 2 * 1024 * 1024;

std::string lower_copy(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    return value;
}

std::string trim_copy(std::string value) {
    const auto first = value.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) return "";
    const auto last = value.find_last_not_of(" \t\r\n");
    return value.substr(first, last - first + 1);
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

std::string sla_status(double score, int age_days) {
    const int limit = score >= 9.0 ? 7 : score >= 7.0 ? 14 : score >= 4.0 ? 30 : 60;
    if (age_days > limit) return "overdue";
    if (age_days >= limit - 3) return "due_soon";
    return "on_track";
}

std::string remediation_priority(double score, int age_days) {
    if (score >= 9.0 || age_days > 30) return "p0";
    if (score >= 7.0 || age_days > 14) return "p1";
    if (score >= 4.0 || age_days > 7) return "p2";
    return "p3";
}

std::vector<std::string> split_csv(const std::string& line) {
    std::vector<std::string> fields;
    std::string current;
    std::stringstream stream(line);
    while (std::getline(stream, current, ',')) {
        fields.push_back(current);
    }
    return fields;
}

void write_portfolio_summary() {
    std::string line;
    int total = 0;
    int open = 0;
    int critical = 0;
    int urgent = 0;
    double risk_sum = 0.0;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        const auto fields = split_csv(line);
        if (fields.size() < 3) continue;
        const std::string severity = lower_copy(fields[0]);
        const double risk = std::stod(fields[1]);
        const std::string status = lower_copy(fields[2]);
        ++total;
        risk_sum += risk;
        if (status != "fixed" && status != "closed") ++open;
        if (severity == "critical" || risk >= 9.0) ++critical;
        if ((severity == "critical" || risk >= 7.0) && status != "fixed" && status != "closed") ++urgent;
    }
    const double average = total == 0 ? 0.0 : risk_sum / total;
    std::cout << "{\"total\":" << total
              << ",\"open\":" << open
              << ",\"critical\":" << critical
              << ",\"urgent\":" << urgent
              << ",\"average_risk\":" << std::fixed << std::setprecision(2) << average
              << "}\n";
}

void write_sla_backlog() {
    std::string line;
    int total = 0;
    int overdue = 0;
    int due_soon = 0;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        const auto fields = split_csv(line);
        if (fields.size() < 4) continue;
        const auto status = lower_copy(fields[2]);
        if (status == "fixed" || status == "closed") continue;
        ++total;
        const auto state = sla_status(std::stod(fields[1]), std::stoi(fields[3]));
        if (state == "overdue") ++overdue;
        if (state == "due_soon") ++due_soon;
    }
    std::cout << "{\"open_sla_items\":" << total
              << ",\"overdue\":" << overdue
              << ",\"due_soon\":" << due_soon
              << "}\n";
}

void write_priority_mix() {
    std::string line;
    int p0 = 0;
    int p1 = 0;
    int p2 = 0;
    int p3 = 0;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        const auto fields = split_csv(line);
        if (fields.size() < 2) continue;
        try {
            const auto priority = remediation_priority(std::stod(trim_copy(fields[0])), std::stoi(trim_copy(fields[1])));
            if (priority == "p0") ++p0;
            else if (priority == "p1") ++p1;
            else if (priority == "p2") ++p2;
            else ++p3;
        } catch (const std::exception&) {
            continue;
        }
    }
    std::cout << "{\"p0\":" << p0 << ",\"p1\":" << p1 << ",\"p2\":" << p2 << ",\"p3\":" << p3 << "}\n";
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
    if (mode == "sla" && argc == 6) {
        const double cvss = std::stod(argv[4]);
        const double score = std::min(cvss * criticality_multiplier(std::stoi(argv[3])) * exposure_multiplier(argv[2]), 10.0);
        std::cout << sla_status(score, std::stoi(argv[5])) << "\n";
        return 0;
    }
    if (mode == "priority" && argc == 6) {
        const double cvss = std::stod(argv[4]);
        const double score = std::min(cvss * criticality_multiplier(std::stoi(argv[3])) * exposure_multiplier(argv[2]), 10.0);
        std::cout << remediation_priority(score, std::stoi(argv[5])) << "\n";
        return 0;
    }
    if (mode == "portfolio" && argc == 2) {
        write_portfolio_summary();
        return 0;
    }
    if (mode == "backlog" && argc == 2) {
        write_sla_backlog();
        return 0;
    }
    if (mode == "priority-mix" && argc == 2) {
        write_priority_mix();
        return 0;
    }
    return 2;
}
// Project version: VulnScope V1.5



