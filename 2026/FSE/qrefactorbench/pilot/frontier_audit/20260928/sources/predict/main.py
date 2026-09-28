from algorithm_selection_framework import *

ideal_file_name = "csvs/ideal_annotations_input.csv"
noisy_file_name = "csvs/noisy_annotations_input.csv"


def main():
    # load ideal or noisy data
    file_name = ideal_file_name
    total_df = pd.read_csv(file_name)

    sizes = total_df["size"].unique()
    n_layer_values = total_df["n_layers"].unique()
    problems = total_df["problem"].unique()
    algorithms = total_df["algorithm"].unique()
    seeds = total_df["seed"].unique()

    prepare_df(total_df)

    def get_variable_value(variable_name, instance, algorithm):
        return get_variable_value_from_df(total_df, variable_name, instance, algorithm)

    def execute_algorithm(algorithm, instance):
        try:
            row = total_df.loc[
                (
                    instance.get_problem_name(),
                    instance.get_number_of_qubits(),
                    instance.seed,
                    algorithm.type,
                    algorithm.n_layers,
                )
            ]
            row = row.copy()
            row["problem"] = instance.get_problem_name()
            row["size"] = instance.get_number_of_qubits()
            row["seed"] = instance.seed
            row["algorithm"] = algorithm.type
            row["n_layers"] = algorithm.n_layers
            return df_row_to_result(row)
        except KeyError:
            return None

    n_initial_rows = 1000
    df = pd.read_csv(file_name, nrows=n_initial_rows)

    db = AlgorithmSelectionFramework(execute_algorithm)
    db.add_results(csv_df_to_results(df))

    while True:
        size = random.choice(sizes)
        problem = random.choice([MaxCut, Partition, Max3Sat, Mis, VertexCover])
        instance = problem.generate_random_instance(size, random.randint(0, 100))

        with maximize(SOLUTION_QUALITY), RUNTIME <= 100:
            result = db.execute_optimal_algorithm(instance, max_n_layers=7)

        with minimize(RUNTIME + 0.5 * RELATIVE_SOLUTION_QUALITY), (
            RELATIVE_SOLUTION_QUALITY >= 0.9
        ) & (RUNTIME <= 100):
            print("Runtime")
            result = db.execute_optimal_algorithm(instance, max_n_layers=7)

        with maximize(SOLUTION_QUALITY_PER_RUNTIME):
            print("Quality per runtime")
            result = db.execute_optimal_algorithm(instance, max_n_layers=7)


if __name__ == "__main__":
    np.seterr(all="ignore")
    main()
