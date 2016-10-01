"""
Common code for tests. The tests themselves are located in ../tests, but need to import this, so...
"""
from copy import deepcopy

import matplotlib
import numpy as np
from scipy import stats

matplotlib.use('agg')
from blueice.source import Source, MonteCarloSource    # noqa


class GaussianSourceBase(Source):
    """Analog of GaussianSource which generates its events by PDF
    """
    events_per_day = 1000

    def simulate(self, n_events):
        d = np.zeros(n_events, dtype=[('x', np.float), ('source', np.int)])
        d['x'] = stats.norm(self.config['mu'], self.config['sigma']).rvs(n_events)
        return d


class GaussianSource(GaussianSourceBase):
    """A 1d source with a Gaussian PDF -- useful for testing
    If your sources are as simple as this, you probably don't need blueice!
    """
    fraction_in_range = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_per_day *= self.config.get('some_multiplier', 1)
        self.events_per_day *= len(self.config.get('strlen_multiplier', 'x'))
        (self.mu, self.sigma) = (self.config.get('mu'), self.config.get('sigma', 1))

    def pdf(self, *args):
        return stats.norm(self.mu, self.sigma).pdf(args[0])


class GaussianMCSource(GaussianSourceBase, MonteCarloSource):
    """Analog of GaussianSource which generates its PDF from MC
    """
    n_events_for_pdf = int(1e6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_per_day *= self.config.get('some_multiplier', 1)
        self.events_per_day *= len(self.config.get('strlen_multiplier', 'x'))
        (self.mu, self.sigma) = (self.config.get('mu'), self.config.get('sigma', 1))
        self.compute_pdf()


BASE_CONFIG = dict(
    sources=[{'name': 's0', 'events_per_day': 1000.}],
    mu=0,
    strlen_multiplier='q',
    sigma=1,
    default_source_class=GaussianSource,
    some_multiplier=1,
    force_pdf_recalculation=True,
    analysis_space=[['x', np.linspace(-10, 10, 100)]]
)


def test_conf(n_sources=1, mc=False):
    conf = deepcopy(BASE_CONFIG)
    conf['sources'] = [{'name': 's%d' % i} for i in range(n_sources)]
    if mc:
        conf['default_source_class'] = GaussianMCSource
    return conf


def almost_equal(a, b, fraction=1e-6):
    return abs((a - b)/a) <= fraction
