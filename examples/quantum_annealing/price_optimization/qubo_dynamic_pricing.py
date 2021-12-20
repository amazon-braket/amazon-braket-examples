from pyqubo import Binary
import numpy as np
import dimod
from braket.ocean_plugin import BraketSampler, BraketDWaveSampler
from dwave.system.composites import EmbeddingComposite
from itertools import combinations

np.random.seed(0)

def get_coeffient(expr, mode):
    coeffs, consts = expr.compile().to_qubo()
    if mode == 'linear':
        new_coeffs = {}
        for k, v in coeffs.items():
            assert k[0] == k[1]
            new_coeffs[k[0]] = v
    elif mode == 'quadratic':
        new_coeffs = coeffs
    else:
        raise TypeError(f"unknown mode: {mode}")

    return new_coeffs, consts


def get_demand(coeff, b, prices):
    assert len(coeff) == len(prices)
    d = b
    for i in range(len(coeff)):
        d += coeff[i]*prices[i]

    return d


def get_variance(data_x, p, sigma):
    """
    :param data_x (np.array): [n_samples, n_days]
    :param p (list): [n_days]
    :return: variance
    """
    n_samples, t = data_x.shape
    ones = np.ones((n_samples, 1), dtype=np.float)
    x_mat = np.concatenate([ones, data_x], axis=1)  # [n_samples, n_days+1]
    x_mat = np.linalg.inv(
        np.dot(x_mat.T, x_mat)
    )
    p = np.array([1.]+p)
    variance = (sigma**2) * (1. + p.dot(x_mat).dot(p))
    return variance


def get_covariance(data_x, p1, p2, sigma):
    """
    :param data_x (np.array): [n_samples, n_days]
    :param p1, p2 (list): [n_days]
    :return: variance
    """
    n_samples, t = data_x.shape
    ones = np.ones((n_samples, 1), dtype=np.float)
    x_mat = np.concatenate([ones, data_x], axis=1)  # [n_samples, n_days+1]
    x_mat = np.linalg.inv(
        np.dot(x_mat.T, x_mat)
    )
    p1 = np.array([1.] + p1)
    p2 = np.array([1.] + p2)
    variance = (sigma**2) * (1. + p1.dot(x_mat).dot(p2))
    return variance


def create_program(a,b, p_data, price_levels, data_x, Lp, Ld, sigma, beta, vol_bound):
    """

    :param a (list of int): [7], coefficient
    :param b (int):
    :param p_data (list of int): [7], past 7 days prices
    :param price_levels (list of int): number of price levels
    :param data_x (np.array): [nsamples, n_days]
    :param L (float): coeff of constraints penalty
    :param sigma (float): standard deviation of noise
    :param beta (float): coeff of variance
    :return:
    """
    assert type(a) is list
    #assert type(b) is int
    assert type(p_data) is list
    assert type(price_levels) is list

    t = len(a)
    n_level = len(price_levels)

    # variables
    x = []
    p = []
    d = []

    # get p
    for i in range(t):
        p_i = 0
        for j in range(n_level):
            x_ij = Binary(f"X_{i*n_level+j:03d}")
            x.append(x_ij)
            p_i += x_ij*price_levels[j]
        p.append(p_i)

    all_p = p_data + p

    # get d, rev
    rev = 0
    for i in range(t):
        d_i = get_demand(
            coeff=a,
            b=b,
            prices=all_p[i+1:i+1+t]
        )
        d.append(d_i)
        rev += d_i * p[i]
        # minus variance
        rev -= beta * get_variance(data_x, all_p[i+1:i+1+t], sigma)
        # add inequaliry constraints
        if vol_bound:
            _, d_const = get_coeffient(d_i, 'linear')
            rev -= inequality_penalty(
                demand=d_i,
                demand_name=f'demand{i}',
                vol_bounday=vol_bound,
                d_const=d_const,
                Ld=Ld
            )

    # add equalty constraints
    for i in range(t):
        penalty = x[i*n_level]
        for j in range(1, n_level):
            penalty += x[i*n_level+j]
        penalty = ((penalty-1)**2)*Lp
        rev -= penalty

    return rev, d


def construct_slack(n, name):
    e = 0
    slack = 0
    while n >= 2**e:
        n -= 2**e
        slack += (2**e) * Binary(f"{name}_{e}")
        e += 1

    slack += n * Binary(f"{name}_{e}")
    return slack


def inequality_penalty(demand, demand_name, vol_bounday, d_const, Ld):
    rhs = vol_bounday - d_const
    assert rhs <= 0
    n = -rhs
    slack = construct_slack(n, demand_name)
    return ((demand-vol_bounday-slack)**2)*Ld


def optimize(
        a,
        b,
        data_x,
        selected_hist_prices,
        price_levels,
        Lp,
        Ld,
        sigma,
        beta,
        vol_bound,
        s3_folder,
        dwave=True
):
    """

    :param a: list of int, coeff
    :param b: int, const
    :param data_x: training set of x
    :param selected_hist_prices: list, last n days prices
    :param price_levels: list of int, options of prices
    :param Lp: int, coeff of price constraints penalty
    :param Ld: int, coeff of demand constraints penalty
    :param sigma: float, stand deviation of noise
    :param beta: float, coeff of variance penalty
    :param vol_bound: float, boundary of demand
    :return:
    """
    obj, demands = create_program(
        a=a,
        b=b,
        p_data=selected_hist_prices,
        price_levels=price_levels,
        data_x=data_x,
        Lp=Lp,
        Ld=Ld,
        sigma=sigma,
        beta=beta,
        vol_bound=vol_bound
    )

    # qubo solver
    response = dwave_solver(obj,s3_folder) if dwave else qubo_solver(obj)
    # get optimal prices
    opt_prices, _, energy = decoder_price_response(response, len(a), price_levels)
    opt_demand, max_revenue = get_demands_rev(a, b, selected_hist_prices, opt_prices)
    prediction_variance = get_overall_variance(data_x, selected_hist_prices, opt_prices, sigma)
    revenue_variance = get_overall_revenue_variance(data_x, selected_hist_prices, opt_prices, sigma)

    return max_revenue, prediction_variance, energy, opt_demand, opt_prices, np.sqrt(revenue_variance)


def qubo_solver(obj):
    model = (-obj).compile().to_bqm()
    num_shots = 100

    sampler = dimod.SimulatedAnnealingSampler()
    response = sampler.sample(model, num_reads=num_shots)
    return response


def dwave_solver(obj,s3_folder):
    model = (-obj).compile().to_bqm()
    num_shots = 10000

    sampler = BraketDWaveSampler(s3_folder,
                                 'arn:aws:braket:::device/qpu/d-wave/Advantage_system4')
    sampler = EmbeddingComposite(sampler)
    response = sampler.sample(model, num_reads=num_shots)
    return response


def decoder_price_response(response, n_days, price_options):
    opt_price, energy = response.record.sample[response.record.energy.argmin()], response.record.energy.min()
    prices = []
    for i in range(n_days):
        price_i = opt_price[i*len(price_options): (i+1)*len(price_options)]
        assert price_i.sum()==1
        prices.append(price_options[price_i.argmax()])
    return prices, opt_price, energy


def get_demands_rev(a, b, hist_p, p):
    all_p = hist_p + p
    t = len(a)
    d = []
    revenue = 0
    for i in range(t):
        d_i = get_demand(
            coeff=a,
            b=b,
            prices=all_p[i+1:i+1+t]
        )
        d.append(d_i)
        revenue += d_i * p[i]
    return d, revenue


def get_overall_variance(data_x, hist_p, p, sigma):
    all_p = hist_p + p
    t = len(p)
    var = 0
    for i in range(t):
        var += get_variance(data_x, all_p[i+1:i+1+t], sigma)

    return var


def get_overall_revenue_variance(data_x, hist_p, p, sigma):
    all_p = hist_p + p
    t = len(p)
    var = 0
    for i in range(t):
        var += get_variance(data_x, all_p[i+1:i+1+t], sigma) * (p[i]**2)

    for i, j in combinations(list(range(t)), 2):
        var += get_covariance(
            data_x,
            all_p[i + 1:i + 1 + t],
            all_p[j + 1:j + 1 + t],
            sigma
        ) * 2 * p[i] * p[j]

    return var
