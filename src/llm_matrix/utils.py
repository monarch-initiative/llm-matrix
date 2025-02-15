from itertools import product

from llm_matrix import Matrix


def iter_hyperparameters(matrix: Matrix):
    """
    Generate all hyperparameter combinations.

    Example:

        >>> matrix = Matrix(hyperparameters={"a": [1, 2], "b": [3, 4]})
        >>> list(iter_hyperparameters(matrix))
        [{'a': 1, 'b': 3}, {'a': 1, 'b': 4}, {'a': 2, 'b': 3}, {'a': 2, 'b': 4}]

    :param matrix:
    :return:
    """
    params = matrix.hyperparameters
    param_names = list(params.keys())
    param_values = list(params.values())

    # Generate all combinations
    combinations = list(product(*param_values))

    # Convert to list of dictionaries
    param_dicts = [
        dict(zip(param_names, combo))
        for combo in combinations
    ]

    yield from param_dicts
