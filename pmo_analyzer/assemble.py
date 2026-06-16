import pandas as pd


def merge_results(df: pd.DataFrame, results: dict[str, dict]) -> pd.DataFrame:
    rows = [{"id": int(k), **v} for k, v in results.items()]
    score_df = pd.DataFrame(rows)
    return df.merge(score_df, on="id", how="left")
