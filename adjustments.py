
def apply_adjustments(df, subject_info, schema):
    subject_sf = float(subject_info.get("Above Grade SF", 0))
    ag_rate = schema.get("Above Grade Finished Area", {}).get("rate", 40)

    df["AG Diff"] = df["Above Grade Finished Area"] - subject_sf
    df["Adj Close Price"] = df["Close Price"] + df["AG Diff"] * ag_rate
    return df
