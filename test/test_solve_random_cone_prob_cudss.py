from __future__ import print_function, division
import scs
import numpy as np
from scipy import sparse
import gen_random_cone_prob as tools

#############################################
#  Uses scs to solve a random cone problem  #
#############################################


def import_error(msg):
    print()
    print("## IMPORT ERROR:" + msg)
    print()


try:
    import pytest
except ImportError:
    import_error("Please install pytest to run tests.")
    raise

np.random.seed(1)

# cone:
K = {
    "z": 10,
    "l": 15,
    "q": [5, 10, 0, 1],
    "s": [3, 4, 0, 0, 1, 10],
    "ep": 10,
    "ed": 10,
    "p": [-0.25, 0.5, 0.75, -0.33],
}
m = tools.get_scs_cone_dims(K)
params = {"verbose": True, "eps_abs": 1e-5, "eps_rel": 1e-5, "eps_infeas": 1e-5}


try:
    from scs import _scs_cudss

    def test_solve_feasible():
        data, p_star = tools.gen_feasible(K, n=m // 3, density=0.1)
        solver = scs.SCS(data, K, cudss=True, **params)
        sol = solver.solve()
        x = sol["x"]
        y = sol["y"]
        s = sol["s"]
        np.testing.assert_almost_equal(np.dot(data["c"], x), p_star, decimal=3)
        np.testing.assert_almost_equal(np.dot(data["c"], x), p_star, decimal=3)
        np.testing.assert_array_less(
            np.linalg.norm(data["A"] @ x - data["b"] + s), 1e-3
        )
        np.testing.assert_array_less(
            np.linalg.norm(data["A"].T @ y + data["c"]), 1e-3
        )
        np.testing.assert_almost_equal(s.T @ y, 0.0)
        np.testing.assert_almost_equal(s, tools.proj_cone(s, K), decimal=4)
        np.testing.assert_almost_equal(y, tools.proj_dual_cone(y, K), decimal=4)

    def test_solve_infeasible():
        data = tools.gen_infeasible(K, n=m // 2)
        solver = scs.SCS(data, K, cudss=True, **params)
        sol = solver.solve()
        y = sol["y"]
        np.testing.assert_array_less(np.linalg.norm(data["A"].T @ y), 1e-3)
        np.testing.assert_array_less(data["b"].T @ y, -0.1)
        np.testing.assert_almost_equal(y, tools.proj_dual_cone(y, K), decimal=4)

    def test_solve_unbounded():
        data = tools.gen_unbounded(K, n=m // 2)
        solver = scs.SCS(data, K, cudss=True, **params)
        sol = solver.solve()
        x = sol["x"]
        s = sol["s"]
        np.testing.assert_array_less(np.linalg.norm(data["A"] @ x + s), 1e-3)
        np.testing.assert_array_less(data["c"].T @ x, -0.1)
        np.testing.assert_almost_equal(s, tools.proj_cone(s, K), decimal=4)

except ImportError:
    import_error("Skipping cuDSS tests as SCS cuDSS is not installed.")
