import numpy as np

def jackknife(data : np.ndarray, func=np.mean, axis=0):
    """Compute jackknife estimate and standard error along a particular axis """
    n = data.shape[axis]
    estimates = [func(np.delete(data, i, axis=axis)) for i in range(n)]
    return np.mean(estimates), np.std(estimates) * np.sqrt(n-1), np.array(estimates)


def jackknife_bias_corrected(data, func=np.mean, axis=0, estimates = False):
    full_est = func(data)
    jack_est, jack_err, estimates = jackknife(data, func, axis)
    bias = (data.shape[axis] - 1) * (jack_est - full_est)

    if estimates:
        return full_est - bias, jack_err, estimates - bias
    return full_est - bias, jack_err



def perform_regression(xs, ys, variances = None, rcond : float = 0.01, error : bool = True) -> float:
    """ perform a logarithmic (or linear) regression of the data and return estimate with potentially error """
    try:
        sgn = -1 if ys[0] < 0 else +1
        coeff, cov = np.polyfit(xs, np.log(np.abs(ys)), 1, rcond=rcond,  w=variances**(-0.5), cov = True)
        ans = np.exp(coeff[1])
        if error: 
            return sgn*ans, np.sqrt(cov[1,1]) * ans
        return sgn * ans
    except Exception as e:
        print(e)
        coeff, cov = np.polyfit(xs, ys, 1, rcond=rcond, cov = True)
        return coeff[1]