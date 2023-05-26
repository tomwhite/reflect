import numba as nb
import numpy as np


# adapted from https://stackoverflow.com/a/64234230
@nb.njit(nb.int32[:, :](nb.int32[:]), cache=True)
def cproduct_idx(sizes: np.ndarray):  # pragma: no cover
    """Generates ids tuples for a cartesian product"""
    # assert len(sizes) >= 2  # restriction not needed
    tuples_count = np.prod(sizes)
    tuples = np.zeros((tuples_count, len(sizes)), dtype=np.int32)
    tuple_idx = 0
    tuple_idx_max = 0
    # stores the current combination
    current_tuple = np.zeros(len(sizes))
    while tuple_idx < tuples_count:
        # only include strictly increasing tuples
        j = 1
        for i in range(0, len(sizes) - 1):
            if current_tuple[i] >= current_tuple[i + 1]:
                j = 0
                break
        if j == 1:
            tuples[tuple_idx_max] = current_tuple
            tuple_idx_max += 1

        current_tuple[0] += 1
        for i in range(0, len(sizes) - 1):
            if current_tuple[i] == sizes[i]:
                # the reset to 0 and subsequent increment amount to carrying
                # the number to the higher "power"
                current_tuple[i + 1] += 1
                current_tuple[i] = 0
            else:
                break
        tuple_idx += 1
    return tuples[:tuple_idx_max]  # only return ones actually stored
