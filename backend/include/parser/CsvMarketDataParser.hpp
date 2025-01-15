#pragma once

#include "MarketDataParser.hpp"

class CsvMarketDataParser : public MarketDataParser {
    public:
        std::vector<MarketData> parse(const std::string& filename) override;
};