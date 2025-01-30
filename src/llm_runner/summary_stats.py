import pandas as pd


def summary_by(df: pd.DataFrame, source_keys: set, group_by="case_input"):
    grouped_df = df.groupby(group_by).aggregate(
        {"score": ["mean", "std", "max", "min", "count"]},
    )
    grouped_df.reset_index(inplace=True, drop=False, col_level=1)
    grouped_df.sort_values([("score", "mean")], ascending=False, inplace=True)
    # Create the quantitative aggregations (across all models)
    score_agg = df.groupby(group_by).agg({
        "score": ["mean", "std", "max", "min", "count"]
    })

    # Create the response text pivot
    text_pivot = df.pivot_table(
        index=group_by,
        columns="hyperparameters",
        values="response_text",
        aggfunc="first"  # Takes the first response for each model
    )

    # Create the score pivot
    score_pivot = df.pivot_table(
        index="case_input",
        columns="hyperparameters",
        values="score",
        aggfunc="first"  # Takes the first response for each model
    )

    other_cols = df.groupby(grouped_df).agg({
        "case_ideal": "first",
        **{k: "first" for k in source_keys},
    })

    # Rename text columns to be clear they're responses
    text_pivot.columns = [f"{col}_response" for col in text_pivot.columns]

    # Flatten the score column names
    score_agg.columns = [f"{col[1]}" for col in score_agg.columns]
    group_by = pd.concat([score_agg, text_pivot, score_pivot, other_cols], axis=1)
    return group_by
