import math
import numpy as np
from scipy.special import logsumexp


def exp2_safe(x):
    return float(2.0 ** x) if math.isfinite(x) and -1074 <= x < 1024 else None


def volume_metrics(n, qs):
    if not len(qs):
        return dict(log2_eager_volume=None, log2_lazy_volume=None, log2_reduction=None,
                    reduction_factor_if_representable=None)
    values = np.asarray(qs, dtype=float)
    lazy = float(logsumexp(values * math.log(2)) / math.log(2))
    eager = math.log2(len(qs)) + n
    reduction = max(0.0, eager - lazy)
    return dict(log2_eager_volume=eager, log2_lazy_volume=lazy, log2_reduction=reduction,
                reduction_factor_if_representable=exp2_safe(reduction))
