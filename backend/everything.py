import pandas
import numpy as np
from datetime import datetime
from scipy.optimize import newton
from scipy.interpolate import interp1d

#1
def price_bond_fixed_rfr(nominal, coupon_rate, maturity_years, rfr):
    coupon = nominal * coupon_rate
    cash_flows = [coupon] * maturity_years
    cash_flows[-1] += nominal
    discounted_cash_flows = [cf / ((1 + rfr) ** (t + 1)) for t, cf in enumerate(cash_flows)]
    return sum(discounted_cash_flows)

#2
def price_bond_variable_rfr(nominal, coupon_rate, maturity_years, rfrs):
    coupon = nominal * coupon_rate
    cash_flows = [coupon] * maturity_years
    cash_flows[-1] += nominal
    discounted_cash_flows = [cf / ((1 + rfrs[t]) ** (t + 1)) for t, cf in enumerate(cash_flows)]
    return sum(discounted_cash_flows)

#3
def price_bond_market_data(nominal, coupon_rate, maturity_years, market_data):
    rfrs = market_data[:maturity_years]
    return price_bond_variable_rfr(nominal, coupon_rate, maturity_years, rfrs)

#4
def interpolate_rfr(market_data, target_year):
    years = list(range(1, len(market_data) + 1))
    return np.interp(target_year, years, market_data)

def price_bond_non_quoted_maturity(nominal, coupon_rate, target_year, market_data):
    interpolated_rfr = interpolate_rfr(market_data, target_year)
    return price_bond_fixed_rfr(nominal, coupon_rate, int(target_year), interpolated_rfr)

#5
def calculate_accrual(coupon_rate, nominal, last_coupon_date, current_date):
    days_in_period = 360 / (1 / coupon_rate)
    days_elapsed = (current_date - last_coupon_date).days
    return (days_elapsed / days_in_period) * (coupon_rate * nominal)

def price_bond_with_accruals(nominal, coupon_rate, maturity_years, rfr, issue_date, current_date):
    bond_price = price_bond_fixed_rfr(nominal, coupon_rate, maturity_years, rfr)
    accrual = calculate_accrual(coupon_rate, nominal, issue_date, current_date)
    return bond_price + accrual, accrual

#############################

def calculate_discount_factor(rate, time):
    """Calculate discount factor for a given rate and time."""
    return 1 / (1 + rate) ** time

def calculate_clean_price_fixed_rate(nominal, coupon_rate, rfr, maturity_years):
    """Calculate clean price of a bond with fixed risk-free rate."""
    # Calculate annual coupon payment
    coupon_payment = nominal * coupon_rate
    
    # Calculate present value of all coupons and final nominal
    present_value = 0
    for year in range(1, maturity_years + 1):
        if year == maturity_years:
            # Last payment includes nominal
            cash_flow = coupon_payment + nominal
        else:
            cash_flow = coupon_payment
        present_value += cash_flow * calculate_discount_factor(rfr, year)
    
    return present_value

def interpolate_rate(x, x_values, y_values):
    """Linear interpolation for rates."""
    return np.interp(x, x_values, y_values)

def calculate_market_rates(bonds_df, valuation_date):
    """Extract and calculate market rates from bonds data."""
    # Convert dates to years from valuation date
    valuation_date = datetime.strptime(valuation_date, '%Y-%m-%d')
    bonds_df['years_to_maturity'] = bonds_df['Maturité'].apply(
        lambda x: (datetime.strptime(x, '%Y-%m-%d') - valuation_date).days / 360
    )
    
    # Get clean prices and calculate yields
    valid_bonds = bonds_df[
        (bonds_df['Prix marché (clean)'].notna()) & 
        (bonds_df['Coupon %'].notna())
    ].copy()
    
    # Sort by maturity
    valid_bonds = valid_bonds.sort_values('years_to_maturity')
    
    return valid_bonds['years_to_maturity'].values, valid_bonds['Prix marché (clean)'].values / 100




def main():
    def f(r, nominal, coupon_rate, maturity_years, market_price):
        return sum([coupon_rate/((1+r)**(i)) for i in range(1, maturity_years+1)])  + nominal  / (1+r)**maturity_years - market_price


    bonds = pandas.read_csv("resources/bonds.csv")

    nominal = 100
    coupons = bonds["Coupon %"]
    maturites = bonds["Maturité"]
    prix = bonds["Prix marché (clean)"]

    # print(coupons, maturites, prix)

    #1
    step1_price = price_bond_fixed_rfr(nominal, 0.04, 5, 0.03)

    #2
    step2_price = price_bond_variable_rfr(100, 0.04, 5, [0.02, 0.025, 0.03, 0.035, 0.04])

    # print(step2_price)

    #3
    rates = []

    r_initial_guess = 0.0

    coupon_rate = 0.045
    maturity_years = 1
    m = 102.17
    rates.append(newton(f, r_initial_guess, args=(nominal, coupon_rate, maturity_years, m)))

    coupon_rate = 0.05
    maturity_years = 2
    m = 105.22
    rates.append(newton(f, r_initial_guess, args=(nominal, coupon_rate, maturity_years, m)))

    coupon_rate = 0.03
    maturity_years = 3
    m = 101.96
    rates.append(newton(f, r_initial_guess, args=(nominal, coupon_rate, maturity_years, m)))

    coupon_rate = 0.01
    maturity_years = 4
    m = 94.93
    rates.append(newton(f, r_initial_guess, args=(nominal, coupon_rate, maturity_years, m)))

    coupon_rate = 0.01
    maturity_years = 5
    m = 93.65
    rates.append(newton(f, r_initial_guess, args=(nominal, coupon_rate, maturity_years, m)))

    print(rates)

    step3_price = price_bond_variable_rfr(100, 0.04, 5, rates)
    print(step3_price)
    
    df = pandas.read_csv("resources/bonds.csv")

    # Initialisation d'une liste pour les taux calculés
    rates = []

    # Supposons que le fichier CSV contient les colonnes 'date', 'market_price', 'nominal', 'coupon_rate' et 'maturity_years'
    for _, row in df.iterrows():
        nominal = row['Nominal']
        coupon_rate = row['Coupon %']
        market_price = row['Prix marché (clean)']
        maturity_date = pandas.to_datetime(row['Maturité'])  # Date de maturité de l'obligation
        maturity_years = int((maturity_date - pandas.to_datetime("2025-01-16")).days / 360)
        # Initialisation de la première estimation du taux
        r_initial_guess = 0.05  # Par exemple, 5% initialement

        # Calcul du taux d'actualisation via la méthode de Newton
        rate = newton(f, r_initial_guess, args=(nominal, coupon_rate, maturity_years, market_price))
        rates.append(rate)

    # Ajouter les taux au dataframe
    df['ytm'] = rates

    # Convertir la colonne 'date' en type datetime si nécessaire
    df['Maturité'] = pandas.to_datetime(df['Maturité'])

   # Interpolation des taux
    # Par exemple, pour une date donnée 'date_to_interpolate':
    date_to_interpolate = pandas.to_datetime('2031-01-16')

    # Convertir les dates de maturité et la date d'interpolation en nombre de jours depuis une référence
    df['maturity_days'] = (df['Maturité'] - pandas.to_datetime('1970-01-01')).dt.days
    date_to_interpolate_days = (date_to_interpolate - pandas.to_datetime('1970-01-01')).days

    # Créer une fonction d'interpolation linéaire à partir des données (maturity_days, taux)
    interp_function = interp1d(df['maturity_days'], df['ytm'], kind='linear', fill_value='extrapolate')

    # Interpolation pour la date donnée
    interpolated_rate = interp_function(date_to_interpolate_days)

    print(interpolated_rate)
    
    # results = {
    #     "step1": step1_price,
    #     "step2": step2_price,
    #     "step3": step3_price,
    #     "step4": step4_price,
    #     "step5": {
    #         "npv": step5_price,
    #         "accrual": step5_accrual
    #     }
    # }

    # Sauvegarde dans un fichier JSON
    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    main()
