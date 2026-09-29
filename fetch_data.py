"""Télécharge les rendements mensuels de FCNTX et des 11 ETF sectoriels SPDR,
et vérifie les rendements annuels contre les chiffres publiés par Fidelity.

Usage : pip install yfinance pandas && python fetch_data.py
"""
import pandas as pd
import yfinance as yf

FUND = "FCNTX"
SECTORS = ["XLK", "XLC", "XLF", "XLY", "XLV", "XLI", "XLP", "XLB", "XLE", "XLU", "XLRE"]
START = "2018-06-25"   # inclut la clôture du 29 juin 2018 comme base (XLC lancé en juin 2018)
END = "2026-09-01"     # borne exclusive : dernier mois complet = août 2026

# Rendements annuels publiés par Fidelity (%), pour contrôle
PUBLISHED = {2019: 29.98, 2020: 32.58, 2021: 24.36, 2022: -28.26,
             2023: 39.33, 2024: 35.97, 2025: 21.80}

tickers = [FUND] + SECTORS
# auto_adjust=True : prix ajustés des dividendes et distributions (total return)
px = yf.download(tickers, start=START, end=END, auto_adjust=True,
                 interval="1d", progress=False)["Close"]

monthly = px.resample("ME").last().pct_change().dropna(how="all")
monthly = monthly.dropna()  # garde uniquement les mois où tout est disponible
monthly.to_csv("monthly_returns.csv")
print(f"{len(monthly)} mois, de {monthly.index[0]:%Y-%m} à {monthly.index[-1]:%Y-%m}")

# Contrôle : composition des rendements mensuels en rendements annuels
annual = (1 + monthly[FUND]).groupby(monthly.index.year).prod() - 1
print("\nAnnée | calculé (%) | publié (%) | écart")
for year, pub in PUBLISHED.items():
    if year in annual.index:
        calc = annual[year] * 100
        print(f"{year}  | {calc:9.2f}   | {pub:8.2f}   | {calc - pub:+.2f}")
