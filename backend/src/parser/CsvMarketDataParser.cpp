#include <iostream>
#include <fstream>
#include <sstream>

#include "CsvMarketDataParser.hpp"

std::vector<MarketData> CsvMarketDataParser::parse(const std::string& filename) {
    std::vector<MarketData> marketDataList;
    std::ifstream file(filename);

    std::string line;
    std::getline(file, line); // Skip the header

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string token;
        MarketData data;

        // Read ISIN
        std::getline(ss, data.isin, ',');

        // Read Name
        std::getline(ss, data.name, ',');

        // Read Nominal Amount
        std::getline(ss, token, ',');
        data.nominalAmount = std::stod(token);

        // Read Maturity Date
        std::getline(ss, token, ',');
        int year = std::stoi(token.substr(0, 4));
        int month = std::stoi(token.substr(4, 6));
        int day = std::stoi(token.substr(6, 8));

        // Read Coupon Rate
        std::getline(ss, token, ',');
        data.couponRate = std::stod(token);

        // Read Payment Frequency
        std::getline(ss, token, ',');
        if (token == "Annual") {
            data.paymentFrequency = PaymentFrequency::Annual;
        }

        // Read Market Price
        std::getline(ss, token, ',');
        data.marketPrice = std::stod(token);

        marketDataList.push_back(data);
    }

    file.close();
    return marketDataList;
}