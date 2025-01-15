#pragma once

#include <string>
#include <ctime>

struct MarketData {
    std::string isin;
    std::string name;
    double nominalAmount;
    Date maturity;
    double couponRate;
    PaymentFrequency paymentFrequency;
    double marketPrice;
};

enum class PaymentFrequency {
    Annual
};

struct Date {
    int year;
    int month;
    int day;
};