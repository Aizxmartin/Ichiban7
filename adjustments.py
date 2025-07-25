
def apply_adjustments(df, subject):
    try:
        subject_sf = float(subject["AG SF"])
    except:
        subject_sf = 0

    adjusted_prices = []
    for _, row in df.iterrows():
        try:
            price = float(row["Close Price"])
            sf = float(row["AG SF"])
            concessions = float(row.get("Concessions", 0))
            net_price = price - concessions
            sf_diff = sf - subject_sf
            adj_price = net_price - (sf_diff * 40)
            adjusted_prices.append(adj_price)
        except Exception:
            adjusted_prices.append(None)
    df["Adj Price"] = adjusted_prices
    return df
