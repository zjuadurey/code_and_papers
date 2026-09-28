import pandas as pd
import scipy as sp
import numpy as np

classical_approximation = pd.read_csv("csvs/classical_approximation_benchmark.csv")
circuit_optimization = pd.concat(
    [
        pd.read_csv("csvs/circuit_optimization_benchmark.csv"),
    ],
    ignore_index=True,
)

classical_approximation.rename(
    columns={
        "runtime": "classical_approximation_runtime",
    },
    inplace=True,
)
circuit_optimization.rename(
    columns={
        "n_qaoa_layers": "n_layers",
        "runtime": "circuit_optimization_runtime",
    },
    inplace=True,
)
print(circuit_optimization.head())


for file_name, extrapolation_size in [
    ("ideal", 12),
    ("noisy", 8),
]:
    df = pd.read_csv(f"csvs/{file_name}.csv")

    df = df.merge(
        classical_approximation,
        on=["problem", "size", "seed"],
        how="left",
    )
    df = df.merge(
        circuit_optimization,
        on=["problem", "size", "seed", "n_layers"],
        how="left",
    )
    print(df.head())

    df.loc[
        ~df["algorithm"].isin(["wsqaoa", "wsinitqaoa"]),
        "classical_approximation_runtime",
    ] = 0

    df["total_runtime"] = (
        df["classical_approximation_runtime"]
        + df["circuit_optimization_runtime"]
        + df["runtime"]
    )

    df["total_depth"] = df["cnot_depth"] * df["n_layers"]

    if "noise_level" in df.columns:
        group_columns = ["problem", "algorithm", "noise_level"]
    else:
        group_columns = ["problem", "algorithm"]

    for group, grouped_df in df.groupby(group_columns):
        filtered_df = grouped_df.dropna(subset=["total_runtime", "total_depth"])
        size = filtered_df["size"]
        n_layers = filtered_df["n_layers"]

        x = filtered_df["total_depth"]
        x_squared = x**2
        log_x = np.log(x)
        y = filtered_df["total_runtime"]
        transformed_x, lmbda_x = sp.stats.boxcox(x)
        transformed_y, lmbda = sp.stats.boxcox(y)

        df.loc[grouped_df.index, "transformed_runtime"] = sp.special.boxcox(
            grouped_df["total_runtime"], lmbda
        )

        A = np.vstack([np.ones_like(x), transformed_x]).T
        box_cox_sol, *_ = np.linalg.lstsq(A, transformed_y)
        box_cox_runtime = sp.special.inv_boxcox(
            box_cox_sol[0]
            + box_cox_sol[1] * sp.special.boxcox(grouped_df["total_depth"], lmbda_x),
            lmbda,
        )
        df.loc[grouped_df.index, "box_cox_runtime"] = box_cox_runtime

        A = np.vstack([np.ones_like(x), np.log(x), np.log(size)]).T
        log_sol, *_ = np.linalg.lstsq(A, np.log(y))
        log_runtime = np.exp(
            log_sol[0]
            + log_sol[1] * np.log(grouped_df["total_depth"])
            + log_sol[2] * np.log(grouped_df["size"])
        )
        df.loc[grouped_df.index, "log_runtime"] = log_runtime

        A = np.vstack([np.ones_like(x), np.log(x)]).T
        log_sol, *_ = np.linalg.lstsq(A, np.log(y))
        log_runtime = np.exp(
            log_sol[0] + log_sol[1] * np.log(grouped_df["total_depth"])
        )
        df.loc[grouped_df.index, "log_runtime"] = log_runtime

        A = np.vstack([np.ones_like(x), x, x_squared]).T
        quad_sol, *_ = np.linalg.lstsq(A, y)

        quad_runtime = (
            quad_sol[0]
            + quad_sol[1] * grouped_df["total_depth"]
            + quad_sol[2] * grouped_df["total_depth"] ** 2
        )
        df.loc[grouped_df.index, "quad_runtime"] = quad_runtime

        A = np.vstack([np.ones_like(x), x]).T
        lin_sol, *_ = np.linalg.lstsq(A, y)

        lin_runtime = lin_sol[0] + lin_sol[1] * grouped_df["total_depth"]
        df.loc[grouped_df.index, "lin_runtime"] = lin_runtime
        box_cox_mse = np.sqrt(
            np.mean((grouped_df["total_runtime"] - box_cox_runtime) ** 2)
        )
        log_mse = np.sqrt(np.mean((grouped_df["total_runtime"] - log_runtime) ** 2))
        quad_mse = np.sqrt(np.mean((grouped_df["total_runtime"] - quad_runtime) ** 2))
        lin_mse = np.sqrt(np.mean((grouped_df["total_runtime"] - lin_runtime) ** 2))

    for column in ["log_runtime"]:
        filtered_df = df[df["size"] >= extrapolation_size]
        relative_error = np.mean(
            np.abs(filtered_df["total_runtime"] - filtered_df[column])
            / filtered_df["total_runtime"]
        )
        rmse = np.sqrt(
            np.mean((filtered_df["total_runtime"] - filtered_df[column]) ** 2)
        )
        print(file_name, column, relative_error)
        for group, grouped_df in df.groupby(["algorithm"]):
            log_rmse = np.sqrt(
                np.mean((grouped_df["total_runtime"] - grouped_df[column]) ** 2)
            )
            relative_error = np.mean(
                np.abs(grouped_df["total_runtime"] - grouped_df[column])
                / grouped_df["total_runtime"]
            )
            print(group, column, relative_error)

    df.to_csv(f"csvs/{file_name}-runtime.csv", index=False)
