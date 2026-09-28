import networkx as nx
import math
import numpy as np
import random
from collections import defaultdict
import scipy as sp
import os
from ideal_model_fitting import (
    beta_fit,
    beta_without_boxcox_fit,
    beta_without_boxcox_predict,
    non_linear_fit,
    non_linear_predict,
)
import warnings
from contextvars import ContextVar


def random_erdos_renyi_graph(size, seed):
    return nx.generators.random_graphs.erdos_renyi_graph(size, 0.5, seed=seed)


class Instance:
    def __init__(self, seed=None):
        self.seed = seed
        self.lower_bound = None
        self.upper_bound = None
        self.cnot_depth = None
        self.cnot_count = None

    def get_problem_name(self):
        raise NotImplementedError

    def estimate_cnot_depth(self):
        raise NotImplementedError

    def estimate_cnot_count(self):
        raise NotImplementedError

    def get_cnot_depth(self):
        if self.cnot_depth is not None:
            return self.cnot_depth
        return self.estimate_cnot_depth()

    def get_cnot_count(self):
        if self.cnot_count is not None:
            return self.cnot_count
        return self.estimate

    def compute_lower_bound(self):
        raise NotImplementedError

    def compute_upper_bound(self):
        raise NotImplementedError

    def get_upper_bound(self):
        if self.upper_bound is None:
            self.upper_bound = self.compute_upper_bound()
        return self.upper_bound

    def get_lower_bound(self):
        if self.lower_bound is None:
            self.lower_bound = self.compute_lower_bound()
        return self.lower_bound

    def get_number_of_qubits(self):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.get_problem_name()}({self.get_number_of_qubits()})"

    @staticmethod
    def generate_random_instance(size, seed):
        raise NotImplementedError


class MaxCut(Instance):
    def __init__(self, graph, seed=None):
        super().__init__(seed)
        self.graph = graph

    def get_problem_name(self):
        return "maxcut"

    def compute_upper_bound(self):
        return len(self.graph.edges)

    def compute_lower_bound(self):
        return 1 / 2 * len(self.graph.edges)

    def get_number_of_qubits(self):
        return len(self.graph.nodes)

    def estimate_cnot_depth(self):
        degree = max(d[1] for d in self.graph.degree)
        return 2 * (degree + 1)

    def estimate_cnot_count(self):
        return 2 * len(self.graph.edges)

    @staticmethod
    def generate_random_instance(size, seed):
        return MaxCut(random_erdos_renyi_graph(size, seed), seed)


class Partition(Instance):
    def __init__(self, numbers: list[int], seed=None):
        super().__init__(seed)
        self.numbers = numbers

    def get_problem_name(self):
        return "partition"

    def compute_upper_bound(self):
        return sum(self.numbers)

    def compute_lower_bound(self, n_tries=1000):
        # random n_tries x len(self.numbers) matrix (-1, 1)
        random_matrix = (
            np.random.randint(0, 2, size=(n_tries, len(self.numbers))) * 2 - 1
        )
        # multiply random_matrix by self.numbers
        random_sums = random_matrix @ np.array(self.numbers)
        expected_deviation = np.sum(np.abs(random_sums)) / n_tries
        return self.get_upper_bound() - expected_deviation

    def get_number_of_qubits(self):
        return len(self.numbers)

    def estimate_cnot_depth(self):
        n = self.get_number_of_qubits()
        if n % 2 == 0:
            return 2 * (n - 1)
        return 2 * n

    def estimate_cnot_count(self):
        n = self.get_number_of_qubits()
        return n * (n - 1)  # / 2 * 2

    def generate_random_instance(size, seed):
        np.random.seed(seed)
        numbers = np.random.rand(size)

        return Partition(numbers, seed)


class Max3Sat(Instance):
    def __init__(self, n_vars, clauses, seed=None):
        super().__init__(seed)
        self.n_vars = n_vars
        self.clauses = clauses

        qubo_graph = self.compute_qubo_graph()
        max_degree = max(len(neighbors) for neighbors in qubo_graph.values())
        n_edges = sum(len(neighbors) for neighbors in qubo_graph.values()) // 2
        self.cnot_depth = 2 * (max_degree + 1)
        self.cnot_count = 2 * n_edges

    def get_problem_name(self):
        return "max_3sat"

    def compute_upper_bound(self):
        return len(self.clauses)

    def compute_lower_bound(self):
        def get_satisfiablity_probability(clause):
            var_dict = {}
            for var, neg in clause:
                if var in var_dict and var_dict[var] != neg:
                    return 1
                var_dict[var] = neg
            return 1 - 1 / 2 ** len(var_dict)

        return sum(get_satisfiablity_probability(clause) for clause in self.clauses)

    def compute_qubo_graph(self):
        graph = {}

        def add_edge(u, v):
            if u not in graph:
                graph[u] = set()
            if v not in graph:
                graph[v] = set()
            graph[u].add(v)
            graph[v].add(u)

        for i, clause in enumerate(self.clauses):
            clause_vars = list({var for var, _ in clause})
            for j, var in enumerate(clause_vars):
                add_edge(str(i), var)
                for k in range(j + 1, len(clause_vars)):
                    var2 = clause_vars[k]
                    add_edge(var, var2)
        return graph

    def get_number_of_qubits(self):
        return self.n_vars + len(self.clauses)

    def estimate_cnot_depth(self):
        return self.cnot_depth

    def estimate_cnot_count(self):
        return self.cnot_count

    @staticmethod
    def generate_random_instance(size, seed):
        n = size
        min_n_vars = 1

        max_n_vars = math.ceil(n // 3)

        rng = np.random.default_rng(seed)
        n_vars = rng.integers(min_n_vars, max_n_vars + 1)

        n_clauses = n - n_vars

        clauses = []
        for _ in range(n_clauses):
            clause = []
            for _ in range(3):
                var = rng.integers(0, n_vars)
                neg = bool(rng.integers(0, 2))
                clause.append((var, neg))
            clauses.append(clause)

        return Max3Sat(n_vars, clauses, seed)


def get_mis_upper_bound(graph):
    n = len(graph)
    m = len(graph.edges)
    # tight combinatoric upper bound (https://www.sciencedirect.com/science/article/pii/S0166218X18304062#b6):
    # Suppose a graph G with n vertices contains an independent set I of size k.
    # The maximum number of edges in G is:
    # - in S - I: (n - k) choose 2
    # - between I and G - I: k (n - k)
    # Solve this for k
    upper_bound = 1 / 2 + math.sqrt(1 / 4 + n**2 - n - 2 * m)
    return upper_bound


class Mis(Instance):
    def __init__(self, graph, seed=None):
        super().__init__(seed)
        self.graph = graph

    def get_problem_name(self):
        return "mis"

    def compute_upper_bound(self):
        return get_mis_upper_bound(self.graph)

    def compute_lower_bound(self, n_tries=1000):
        size_sum = 0

        def evaluate_mis(selected_nodes):
            for i, u in enumerate(selected_nodes):
                for j in range(i + 1, len(selected_nodes)):
                    v = selected_nodes[j]
                    if u != v and self.graph.has_edge(u, v):
                        return False
            return True

        for _ in range(n_tries):
            selected_nodes = list(
                {node for node in self.graph.nodes if random.random() > 0.5}
            )
            if evaluate_mis(selected_nodes):
                size_sum += len(selected_nodes)
            else:
                size_sum += 1
        return size_sum / n_tries

    def get_number_of_qubits(self):
        return len(self.graph.nodes)

    def estimate_cnot_depth(self):
        return 2 * (max(d[1] for d in self.graph.degree) + 1)

    def estimate_cnot_count(self):
        return 2 * len(self.graph.edges)

    @staticmethod
    def generate_random_instance(size, seed):
        return Mis(random_erdos_renyi_graph(size, seed), seed)


class VertexCover(Instance):
    def __init__(self, graph, seed=None):
        super().__init__(seed)
        self.graph = graph

    def get_problem_name(self):
        return "vertex_cover"

    def compute_upper_bound(self):
        return 1 / (len(self.graph) - get_mis_upper_bound(self.graph))

    def compute_lower_bound(self, n_tries=1000):
        size_sum = 0

        def evaluate_mis(selected_nodes):
            for i, u in enumerate(selected_nodes):
                for j in range(i + 1, len(selected_nodes)):
                    v = selected_nodes[j]
                    if u != v and self.graph.has_edge(u, v):
                        return False
            return True

        for _ in range(n_tries):
            selected_nodes = list(
                {node for node in self.graph.nodes if random.random() > 0.5}
            )
            if evaluate_mis(selected_nodes):
                size_sum += 1 / (len(self.graph) - len(selected_nodes))
            else:
                size_sum += 1 / len(self.graph)
        return size_sum / n_tries

    def get_number_of_qubits(self):
        return len(self.graph.nodes)

    def estimate_cnot_depth(self):
        return 2 * (max(d[1] for d in self.graph.degree) + 1)

    def estimate_cnot_count(self):
        return 2 * len(self.graph.edges)

    @staticmethod
    def generate_random_instance(size, seed):
        return VertexCover(random_erdos_renyi_graph(size, seed), seed)


class Algorithm:
    def __init__(self, type: str, n_layers: int):
        self.type = type
        self.n_layers = n_layers

    def __repr__(self):
        return f"Algorithm({self.type}, {self.n_layers})"


class QuantumSystem:
    def __init__(self, noise_level, cnot_duration, measurement_duration):
        self.noise_level = noise_level
        self.cnot_duration = cnot_duration
        self.measurement_duration = measurement_duration


class Result:
    def __init__(
        self, algorithm: Algorithm, instance: Instance, solution_quality, runtime
    ):
        self.algorithm = algorithm
        self.instance = instance
        self.solution_quality = solution_quality
        self.runtime = runtime

    def get_group(self):
        return self.algorithm.type, self.instance.get_problem_name()

    def __repr__(self):
        return f"Result({self.algorithm}, {self.instance}, sol={self.solution_quality}, time={self.runtime})"


objective_var = ContextVar("objective")
constraint_group_var = ContextVar("constraint_groups", default=[])


class Term:
    def __init__(self, variable_name, factor):
        self.variable_name = variable_name
        self.factor = factor

    def __repr__(self):
        if self.factor == 1:
            return f"{self.variable_name}"
        if self.factor == -1:
            return f"-{self.variable_name}"
        return f"{self.factor} * {self.variable_name}"


class Expression:
    def __init__(self, *terms):
        self.terms = list(terms)

    def __repr__(self):
        return " + ".join(map(str, self.terms))

    def __le__(self, value):
        return ConstraintGroup(Constraint(self, value, "<="))

    def __ge__(self, value):
        return ConstraintGroup(Constraint(self, value, ">="))

    def __add__(self, other):
        return Expression(*self.terms, *other.terms)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, factor):
        return Expression(
            *[Term(term.variable_name, term.factor * factor) for term in self.terms]
        )

    def __neg__(self):
        return self.__mul__(-1)

    def __rmul__(self, other):
        return self.__mul__(other)


class MinimizeObjective:
    def __init__(self, expr):
        self.expr = expr

    def __enter__(self):
        self.prev = objective_var.set(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        objective_var.reset(self.prev)

    def __repr__(self):
        return f"MinimizeObjective({self.expr})"


def minimize(expr):
    return MinimizeObjective(expr)


def maximize(expr):
    return MinimizeObjective(-expr)


class Constraint:
    def __init__(self, expr, value, operator):
        self.expr = expr
        self.value = value
        self.operator = operator

    def __repr__(self):
        return f"Constraint({self.expr} {self.operator} {self.value})"


class ConstraintGroup:
    def __init__(self, *constraints):
        self.constraints = list(constraints)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def __and__(self, other):
        return ConstraintGroup(*self.constraints, *other.constraints)

    def __enter__(self):
        prev = constraint_group_var.get([])
        constraint_group_var.set(prev + self.constraints)

    def __exit__(self, exc_type, exc_value, traceback):
        prev = constraint_group_var.get([])
        constraint_group_var.set(prev[: -len(self.constraints)])

    def __repr__(self):
        return f"ConstraintGroup({self.constraints})"


def variable_expr(name):
    return Expression(Term(name, 1))


RUNTIME = variable_expr("runtime")
SOLUTION_QUALITY = variable_expr("solution_quality")
RELATIVE_SOLUTION_QUALITY = variable_expr("relative_solution_quality")
SOLUTION_QUALITY_PER_RUNTIME = variable_expr("solution_quality_per_runtime")
RELATIVE_SOLUTION_QUALITY_PER_RUNTIME = variable_expr(
    "relative_solution_quality_per_runtime"
)
RUNTIME_PER_SOLUTION_QUALITY = variable_expr("runtime_per_solution_quality")
RUNTIME_PER_RELATIVE_SOLUTION_QUALITY = variable_expr(
    "runtime_per_relative_solution_quality"
)

variables = [
    RUNTIME,
    SOLUTION_QUALITY,
    RELATIVE_SOLUTION_QUALITY,
    SOLUTION_QUALITY_PER_RUNTIME,
    RELATIVE_SOLUTION_QUALITY_PER_RUNTIME,
    RUNTIME_PER_SOLUTION_QUALITY,
    RUNTIME_PER_RELATIVE_SOLUTION_QUALITY,
]
solution_quality_variables = {
    SOLUTION_QUALITY,
    RELATIVE_SOLUTION_QUALITY,
    SOLUTION_QUALITY_PER_RUNTIME,
    RELATIVE_SOLUTION_QUALITY_PER_RUNTIME,
    RUNTIME_PER_SOLUTION_QUALITY,
    RUNTIME_PER_RELATIVE_SOLUTION_QUALITY,
}

runtime_variables = {
    RUNTIME,
    SOLUTION_QUALITY_PER_RUNTIME,
    RELATIVE_SOLUTION_QUALITY_PER_RUNTIME,
    RUNTIME_PER_SOLUTION_QUALITY,
    RUNTIME_PER_RELATIVE_SOLUTION_QUALITY,
}

variable_name_to_expr = {expr.terms[0].variable_name: expr for expr in variables}


import pandas as pd

problem_map = {
    "maxcut": MaxCut,
    "partition": Partition,
    "max_3sat": Max3Sat,
    "mis": Mis,
    "vertex_cover": VertexCover,
}


def train_beta_model(results, start_params=None):
    size = np.array([result.instance.get_number_of_qubits() for result in results])
    n_layers = np.array([result.algorithm.n_layers for result in results])
    upper_bound = np.array([result.instance.get_upper_bound() for result in results])
    lower_bound = np.array([result.instance.get_lower_bound() for result in results])
    performance = np.array([result.solution_quality for result in results])
    df = pd.DataFrame(
        {
            "size": size,
            "n_layers": n_layers,
            "random_performance": lower_bound / upper_bound,
            "performance": performance / upper_bound,
        }
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return beta_without_boxcox_fit(df, start_params)


def train_power_law_model(results, start_params=None):
    size = np.array([result.instance.get_number_of_qubits() for result in results])
    n_layers = np.array([result.algorithm.n_layers for result in results])
    upper_bound = np.array([result.instance.get_upper_bound() for result in results])
    lower_bound = np.array([result.instance.get_lower_bound() for result in results])
    performance = np.array([result.solution_quality for result in results])
    df = pd.DataFrame(
        {
            "size": size,
            "n_layers": n_layers,
            "random_performance": lower_bound / upper_bound,
            "performance": performance / upper_bound,
        }
    )
    smallest_size = df["size"].min()
    baseline_df = df[df["size"] == smallest_size]

    baseline_df = (
        baseline_df.groupby("n_layers")[["random_performance", "performance"]]
        .mean()
        .rename(
            columns={
                "random_performance": "baseline_random_performance",
                "performance": "baseline_performance",
            }
        )
    )
    df = df.join(baseline_df, on="n_layers")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return tuple(
            [
                *non_linear_fit(df, smallest_size, start_params),
                smallest_size,
                baseline_df,
            ]
        )


def train_linear_runtime_model(results: list[Result]):
    x = np.array(
        [
            result.instance.get_cnot_depth() * result.algorithm.n_layers
            for result in results
        ]
    )
    y = np.array([result.runtime for result in results])
    A = np.vstack([np.ones_like(x), x]).T
    return np.linalg.lstsq(A, y, rcond=None)[0]


def train_quadratic_runtime_model(results: list[Result]):
    x = np.array(
        [
            result.instance.get_cnot_depth() * result.algorithm.n_layers
            for result in results
        ]
    )
    y = np.array([result.runtime for result in results])
    A = np.vstack([np.ones_like(x), x, x**2]).T
    return np.linalg.lstsq(A, y, rcond=None)[0]


def train_log_runtime_model(results: list[Result]):
    x = np.array(
        [
            result.instance.get_cnot_depth() * result.algorithm.n_layers
            for result in results
        ]
    )
    y = np.array([result.runtime for result in results])
    A = np.vstack([np.ones_like(x), np.log(x)]).T
    return np.linalg.lstsq(A, np.log(y), rcond=None)[0]


class AlgorithmSelectionFramework:
    def __init__(self, execute_algorithm):
        self.results = []
        self.solution_quality_parameters = defaultdict(dict)
        self.solution_quality_errors = defaultdict(dict)
        self.results_by_group = defaultdict(list)
        self.runtime_parameters = defaultdict(dict)
        self.execute_algorithm = execute_algorithm

    def _add_result(self, result: Result):
        self.results.append(result)
        self.results_by_group[result.get_group()].append(result)

    def add_result(self, result: Result):
        self._add_result(result)
        self.retrain_model([result.get_group()])

    def add_results(self, results: list[Result]):
        groups = set()
        for result in results:
            self._add_result(result)
            groups.add(result.get_group())
        self.retrain_model(groups)

    def retrain_model(self, groups=None):

        if groups is None:
            groups = self.results_by_group.keys()
        for group in groups:
            self.solution_quality_parameters[group]["beta"] = train_beta_model(
                self.results_by_group[group],
                self.solution_quality_parameters[group].get("beta"),
            )
            self.solution_quality_parameters[group]["power_law"] = (
                train_power_law_model(
                    self.results_by_group[group],
                    self.solution_quality_parameters[group].get("power_law"),
                )
            )
            self.runtime_parameters[group]["linear"] = train_linear_runtime_model(
                self.results_by_group[group]
            )
            self.runtime_parameters[group]["quadratic"] = train_quadratic_runtime_model(
                self.results_by_group[group]
            )

    def select_solution_quality_model(self, algorithm, instance):
        group = (algorithm.type, instance.get_problem_name())
        if group not in self.solution_quality_parameters:
            return None
        if instance.get_problem_name() in ["vertex_cover", "partition"]:
            if "beta" in self.solution_quality_parameters[group]:
                return "beta"
            if "power_law" in self.solution_quality_parameters[group]:
                return "power_law"
            return None

        if "power_law" in self.solution_quality_parameters[group]:
            baseline_df = self.solution_quality_parameters[group]["power_law"][-1]
            if algorithm.n_layers in baseline_df.index:
                return "power_law"

        if "beta" in self.solution_quality_parameters[group]:
            return "beta"

    def select_runtime_model(self, algorithm, instance):
        group = (algorithm.type, instance.get_problem_name())
        if group not in self.runtime_parameters:
            return None
        if "log" in self.runtime_parameters[group]:
            return "log"
        if algorithm.type == "rqaoa":
            if "quadratic" in self.runtime_parameters[group]:
                return "quadratic"
            if "linear" in self.runtime_parameters[group]:
                return "linear"
            return None
        else:
            if "linear" in self.runtime_parameters[group]:
                return "linear"
            if "quadratic" in self.runtime_parameters[group]:
                return "quadratic"
            return None

    def predict_solution_quality(self, algorithm, instance):
        model = self.select_solution_quality_model(algorithm, instance)
        group = (algorithm.type, instance.get_problem_name())

        if model == "beta":
            parameters = self.solution_quality_parameters[group]["beta"]
            random_performance = (
                instance.compute_lower_bound() / instance.get_upper_bound()
            )
            size = instance.get_number_of_qubits()
            n_layers = algorithm.n_layers
            return (
                beta_without_boxcox_predict(
                    parameters[:4],
                    random_performance,
                    size,
                    n_layers,
                )
                * instance.get_upper_bound()
            )

        if model == "power_law":
            parameters = self.solution_quality_parameters[group]["power_law"]
            random_performance = (
                instance.compute_lower_bound() / instance.get_upper_bound()
            )
            size = instance.get_number_of_qubits()
            n_layers = algorithm.n_layers
            smallest_size = parameters[-2]
            baseline_df = parameters[-1]
            baseline_performance = baseline_df.loc[
                algorithm.n_layers, "baseline_performance"
            ]
            baseline_random_performance = baseline_df.loc[
                algorithm.n_layers, "baseline_random_performance"
            ]
            result = (
                non_linear_predict(
                    parameters[:6],
                    random_performance,
                    baseline_performance,
                    baseline_random_performance,
                    n_layers,
                    size,
                    smallest_size,
                )
                * instance.get_upper_bound()
            )[0]
            return result

    def predict_runtime(self, algorithm, instance):
        model = self.select_runtime_model(algorithm, instance)
        group = (algorithm.type, instance.get_problem_name())

        total_depth = instance.get_cnot_depth() * algorithm.n_layers

        if model == "linear":
            parameters = self.runtime_parameters[group]["linear"]
            return parameters[0] + parameters[1] * total_depth

        if model == "quadratic":
            parameters = self.runtime_parameters[group]["quadratic"]
            return (
                parameters[0]
                + parameters[1] * total_depth
                + parameters[2] * total_depth**2
            )

        if model == "log":
            parameters = self.runtime_parameters[group]["log"]
            return np.exp(parameters[0] + parameters[1] * np.log(total_depth))

    def predict_variable_value(self, variable_name, instance, algorithm):
        expr = variable_name_to_expr[variable_name]
        if expr == RUNTIME:
            return self.predict_runtime(algorithm, instance)
        if expr == SOLUTION_QUALITY:
            return self.predict_solution_quality(algorithm, instance)
        if expr == RELATIVE_SOLUTION_QUALITY:
            return (
                self.predict_solution_quality(algorithm, instance)
                / instance.get_upper_bound()
            )
        if expr == SOLUTION_QUALITY_PER_RUNTIME:
            return self.predict_solution_quality(
                algorithm, instance
            ) / self.predict_runtime(algorithm, instance)
        if expr == RELATIVE_SOLUTION_QUALITY_PER_RUNTIME:
            return (
                self.predict_solution_quality(algorithm, instance)
                / instance.get_upper_bound()
                / self.predict_runtime(algorithm, instance)
            )
        if expr == RUNTIME_PER_SOLUTION_QUALITY:
            return self.predict_runtime(
                algorithm, instance
            ) / self.predict_solution_quality(algorithm, instance)
        if expr == RUNTIME_PER_RELATIVE_SOLUTION_QUALITY:
            return (
                self.predict_runtime(algorithm, instance)
                / self.predict_solution_quality(algorithm, instance)
                * instance.get_upper_bound()
            )

    def predict_optimal_algorithm(self, instance, max_n_layers=1000):
        objective = objective_var.get()
        constraint_group = constraint_group_var.get()

        variable_names = [term.variable_name for term in objective.expr.terms] + [
            term.variable_name
            for constraint in constraint_group
            for term in constraint.expr.terms
        ]
        involves_runtime = any(
            variable_name_to_expr[variable_name] in runtime_variables
            for variable_name in variable_names
        )
        involves_solution_quality = any(
            variable_name_to_expr[variable_name] in solution_quality_variables
            for variable_name in variable_names
        )
        algorithms_with_runtime = {alg for alg, prob in self.runtime_parameters}
        algorithms_with_solution_quality = {
            alg for alg, prob in self.solution_quality_parameters
        }

        if involves_runtime and involves_solution_quality:
            algorithms = algorithms_with_runtime & algorithms_with_solution_quality
        elif involves_runtime:
            algorithms = algorithms_with_runtime
        elif involves_solution_quality:
            algorithms = algorithms_with_solution_quality
        else:
            return None, None

        return predict_optimal_algorithm(
            instance, algorithms, self.predict_variable_value, max_n_layers
        )

    def execute_optimal_algorithm(self, instance, max_n_layers=1000):
        optimal_algorithm, predicted_objective = self.predict_optimal_algorithm(
            instance, max_n_layers
        )
        successful = optimal_algorithm is not None
        if optimal_algorithm is None:
            print("no algorithm found, fallback to QAOA (p=1)")
            optimal_algorithm = Algorithm("qaoa", 1)
        result = self.execute_algorithm(optimal_algorithm, instance)
        if result is not None:
            self.add_result(result)
            achieved_objective = predict_expression_value(
                objective_var.get().expr,
                optimal_algorithm,
                instance,
                get_variable_value_from_result(result),
            )
            print(result)
            if successful:
                print(f"Predicted {predicted_objective}, achieved {achieved_objective}")
            else:
                print(f"Achieved {achieved_objective}")
        else:
            print(f"Error executing algorithm {optimal_algorithm}")
        print("--------------------------")
        return result


def predict_expression_value(expr, algorithm, instance, predict_variable_value):
    return sum(
        term.factor * predict_variable_value(term.variable_name, instance, algorithm)
        for term in expr.terms
    )


def predict_optimal_algorithm(
    instance, algorithms, predict_variable_value, max_n_layers=1000
):
    objective = objective_var.get()
    constraint_group = constraint_group_var.get()

    best_objective = math.inf
    best_algorithm = None

    for algorithm_type in algorithms:

        def objective_fun(n_layers):
            if type(n_layers) == np.ndarray:
                n_layers = n_layers[0]
            algorithm = Algorithm(algorithm_type, n_layers)
            return predict_expression_value(
                objective.expr, algorithm, instance, predict_variable_value
            )

        constraints = []

        for constraint in constraint_group:
            if constraint.operator == "<=":
                lb, ub = -math.inf, constraint.value
            elif constraint.operator == ">=":
                lb, ub = constraint.value, math.inf
            else:
                raise ValueError(f"Unsupported operator {constraint.operator}")

            def constraint_fun(n_layers):
                if type(n_layers) == np.ndarray:
                    n_layers = n_layers[0]
                algorithm = Algorithm(algorithm_type, n_layers)
                return predict_expression_value(
                    constraint.expr, algorithm, instance, predict_variable_value
                )

            constraints.append(
                sp.optimize.NonlinearConstraint(
                    constraint_fun,
                    lb=lb,
                    ub=ub,
                )
            )

        result = sp.optimize.minimize(
            fun=objective_fun,
            x0=1,
            bounds=[(1, max_n_layers)],
            constraints=constraints,
        )

        x = result.x[0]

        feasible_results = []
        if int(x) == x:
            algorithm = Algorithm(algorithm_type, int(x))
            feasible_results.append((algorithm, result.fun))
        else:
            for n_layers in [int(x), int(x) + 1]:
                if all(c.lb <= c.fun(n_layers) <= c.ub for c in constraints):
                    feasible_results.append(
                        (
                            Algorithm(algorithm_type, n_layers),
                            objective_fun(n_layers),
                        )
                    )

        for algorithm, obj in feasible_results:
            if obj < best_objective:
                best_objective = obj
                best_algorithm = algorithm

    return best_algorithm, best_objective


def df_row_to_result(row):
    algorithm_type = row["algorithm"]
    n_layers = row["n_layers"]
    problem = row["problem"]
    size = row["size"]
    seed = row["seed"]
    cnot_depth = row["cnot_depth"]
    upper_bound = row["absolute_upper_bound"]
    relative_upper_bound = row["upper_bound"]
    performance = row["performance"]
    runtime = row["runtime"]

    algorithm = Algorithm(algorithm_type, n_layers)
    problem_class = problem_map[problem]
    instance = problem_class.generate_random_instance(size, seed)
    instance.cnot_depth = cnot_depth

    upper_bound_csv = row["absolute_upper_bound"]
    upper_bound = instance.get_upper_bound()

    if not np.isclose(upper_bound_csv, upper_bound):
        print("upper bound mismatch")
        print(upper_bound)
        print(row)

    absolute_performance = performance / relative_upper_bound * upper_bound

    return Result(
        algorithm,
        instance,
        absolute_performance,
        row["runtime"],
    )


def csv_df_to_results(df):
    results = []

    for i, row in df.iterrows():
        results.append(df_row_to_result(row))
    return results


import time


def prepare_df(df):
    df["absolute_performance"] = (
        df["performance"] / df["upper_bound"] * df["absolute_upper_bound"]
    )
    df["relative_performance"] = df["absolute_performance"] / df["absolute_upper_bound"]
    df.set_index(["problem", "size", "seed", "algorithm", "n_layers"], inplace=True)


def get_variable_value_from_df(df, variable_name, instance, algorithm):
    try:
        n_layers = float(algorithm.n_layers)
        rounded_n_layers_values = [int(n_layers), int(n_layers) + 1]
    except ValueError:
        return math.nan

    value_sum = 0

    for rounded_n_layers in rounded_n_layers_values:
        try:
            row = df.loc[
                (
                    instance.get_problem_name(),
                    instance.get_number_of_qubits(),
                    instance.seed,
                    algorithm.type,
                    rounded_n_layers,
                )
            ]
        except KeyError:
            continue

        variable = variable_name_to_expr[variable_name]
        weight = 1 - abs(n_layers - rounded_n_layers)

        if variable == RUNTIME:
            value = row["runtime"]
        elif variable == SOLUTION_QUALITY:
            value = row["absolute_performance"]
        elif variable == RELATIVE_SOLUTION_QUALITY:
            value = row["relative_performance"]
        elif variable == SOLUTION_QUALITY_PER_RUNTIME:
            value = row["absolute_performance"] / row["runtime"]
        elif variable == RELATIVE_SOLUTION_QUALITY_PER_RUNTIME:
            value = row["relative_performance"] / row["runtime"]
        elif variable == RUNTIME_PER_SOLUTION_QUALITY:
            value = row["runtime"] / row["absolute_performance"]
        elif variable == RUNTIME_PER_RELATIVE_SOLUTION_QUALITY:
            value = row["runtime"] / row["relative_performance"]
        else:
            raise ValueError(f"Unknown variable {variable_name}")
        value_sum += value * weight

    return value_sum


def get_variable_value_from_result(result):
    def f(variable_name, *_):
        if variable_name == "runtime":
            return result.runtime
        if variable_name == "solution_quality":
            return result.solution_quality
        if variable_name == "relative_solution_quality":
            return result.solution_quality / result.instance.get_upper_bound()
        if variable_name == "solution_quality_per_runtime":
            return result.solution_quality / result.runtime
        if variable_name == "relative_solution_quality_per_runtime":
            return (
                result.solution_quality
                / result.instance.get_upper_bound()
                / result.runtime
            )
        if variable_name == "runtime_per_solution_quality":
            return result.runtime / result.solution_quality
        if variable_name == "runtime_per_relative_solution_quality":
            return (
                result.runtime
                / result.solution_quality
                * result.instance.get_upper_bound()
            )
        raise ValueError(f"Unknown variable {variable_name}")

    return f
