def calculate_adjustments(df, subject_sf):
    df["AG Diff"] = df["Above Grade Finished Area"] - subject_sf
    df["Total Adj"] = df["AG Diff"] * 40  # $40 per SF
    df["Adjusted Price"] = df["Close Price"] + df["Total Adj"]
    df["Adjusted PPSF"] = df["Adjusted Price"] / df["Above Grade Finished Area"]
    return df