import numpy as np


def jackknife(data : np.ndarray, func=np.mean, axis=0):
    """Compute jackknife estimate and standard error along a particular axis """
    n = data.shape[axis]
    estimates = [func(np.delete(data, i, axis=axis)) for i in range(n)]
    mu = np.mean(estimates)
    var = (n-1)/n * np.sum((estimates - mu)**2)
    return mu, np.sqrt(var), np.array(estimates)


def jackknife_bias_corrected(data, func=np.mean, axis=0, jk_estimates : bool = False):
    full_est = func(data)
    jack_est, jack_err, estimates = jackknife(data, func, axis)
    bias = (data.shape[axis] - 1) * (jack_est - full_est)
    if jk_estimates:
        return full_est - bias, jack_err, estimates - bias
    return full_est - bias, jack_err

def perform_regression_ols(xs, ys, variances = None, rcond : float = 0.01, error : bool = True) -> float:
    """ perform a logarithmic (or linear) regression of the data and return estimate with potentially error """
    var = np.array(variances)
    coeff, cov = np.polyfit(xs, ys, 1, w=1/np.sqrt(var), rcond=rcond, cov = True)
    if error:
        return coeff[1], np.sqrt(cov[1, 1])
    return coeff[1]

def perform_regression_with_resampling(xs,ys,variances):
    errors = np.sqrt(variances)
    trials = 50
    extrapolates = []
    for _ in range(trials):
        y_temp = np.random.normal(ys,errors)
        print('resampled: ',ys,y_temp)
        extrapolates.append(perform_regression(xs,y_temp,variances,error = False))
    print(extrapolates)
    return np.median(extrapolates)

def perform_regression(xs, ys, variances = None, rcond : float = 0.03, error : bool = True) -> float:
    """ perform a logarithmic (or linear) regression of the data and return estimate with potentially error """
    try:
        sgn = -1 if ys[0] < 0 else +1
        # non-monotonic, default to a linear extrapolation 
        sigma = np.sqrt(variances)
        for k in range(len(ys)-1):
            if sgn*ys[k] + sigma[k] < sgn*ys[k+1]-sigma[k+1]:
                raise ValueError(f"non-monotonic {ys} - reverting to OLS")

        var  = np.divide(variances,np.abs(ys)**2)
        coeff, cov = np.polyfit(xs, np.log(np.abs(ys)), 1, rcond=rcond,  w=1/np.sqrt(var), cov = True)
        ans = np.exp(coeff[1])
        if coeff[1] > 0.1:
            raise ValueError(f"exp reg coeff {coeff[1]} is not positive, performing linear regression")
        if error: 
            return sgn*ans, np.sqrt(cov[1,1]) * ans
        return sgn * ans
    except ValueError as e:
        print(f'escaping...{e}')
        var = np.array(variances)
        coeff, cov = np.polyfit(xs, ys, 1, w=1/np.sqrt(var), rcond=rcond, cov = True)
        if error:
            return coeff[1], np.sqrt(cov[1, 1])
        return coeff[1]

if __name__ == "__main__":
    test = np.random.normal(0,1,100)
    mean, sig = jackknife_bias_corrected(test, axis=0)
    original = sig*10
    print(mean,sig)
    print(original)
