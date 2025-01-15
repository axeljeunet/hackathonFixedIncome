#pragma once

#include <string>
#include <vector>
#include <model/MarketData.hpp>

class MarketDataParser {
    public:
        virtual ~MarketDataParser() {}
        virtual std::vector<MarketData> parse(const std::string& filename) = 0;
};