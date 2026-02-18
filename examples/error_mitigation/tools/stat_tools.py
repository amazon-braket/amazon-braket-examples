import numpy as np


def jackknife(data : np.ndarray, func=np.mean, axis=0) -> tuple[float, float, np.ndarray]:
    """Compute jackknife estimate and standard error along a single numpy axis 
    
    Arguments:
        data : numpy array of data

    Keyword arguments: 
        func : function to compute from data (default: mean)
        axis : axis along which to perform the jackknife estimate

    Returns:
        mu (float) : mean estimate
        error (float) : standard error
        estimates (np.ndarray) : all jackknife estimates
    """
    n = data.shape[axis]
    estimates = [func(np.delete(data, i, axis=axis)) for i in range(n)]
    mu = np.mean(estimates)
    var = (n-1)/n * np.sum((estimates - mu)**2)
    return mu, np.sqrt(var), np.array(estimates)


def jackknife_bias_corrected(data, func=np.mean, axis=0, jk_estimates : bool = False
                             ) -> tuple[float, float] | tuple[float, float, np.ndarray]:
    """ Compute bias correction for jackknife estimate, more relevant for small n 
    
    Arguments: 

        Arguments:
        data : numpy array of data

    Keyword arguments: 
        func : function to compute from data (default: mean)
        axis : axis along which to perform the jackknife estimate
        jk_estimates : whether or not to return jackkife estimates 
    
    Returns:
        mu (float) : mean estimate
        error (float) : standard error
        estimates (np.ndarray) : (optional) jackknife estimates

    """
    full_est = func(data)
    jack_est, jack_err, estimates = jackknife(data, func, axis)
    bias = (data.shape[axis] - 1) * (jack_est - full_est)
    if jk_estimates:
        return full_est - bias, jack_err, estimates - bias
    return full_est - bias, jack_err

def perform_regression_ols(xs, ys, variances = None, rcond : float = 0.01, error : bool = True) -> float:
    """ perform a ordinary least squares regression and return estimate with potentially std dev 
    
    Arguments:
        xs : numpy array of independent variables
        ys : numpy array of predictors 

    Keyword arguments: 
        variances : variance of each estimate
        rcond : conditioning number for the fit -> fed to numpy polyfit
        error : whether to return error estimate (std dev) 

    """
    var = np.array(variances)
    coeff, cov = np.polyfit(xs, ys, 1, w=1/np.sqrt(var), rcond=rcond, cov = True)
    if error:
        return coeff[1], np.sqrt(cov[1, 1])
    return coeff[1]

def perform_regression(xs : np.ndarray, ys : np.ndarray, variances : np.ndarray | None = None, rcond : float = 0.03, error : bool = True) -> float:
    """ perform a logarithmic (or linear) regression of the data and return estimate with potentially error 
    
    Arguments:
        xs : numpy array of independent variables
        ys : numpy array of predictors 

    Keyword arguments: 
        variances : variance of each estimate, necessary for log transform 
        rcond : conditioning number for the fit -> fed to numpy polyfit
        error : whether to return error estimate (std dev) 
    """
    try:
        sgn = -1 if ys[0] < 0 else +1
        # non-monotonic, default to a linear extrapolation 
        if variances is None:
            raise ValueError("No variances provided - reverting to OLS")
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
        weights = 1/np.sqrt(variances) if variances is not None else None
        coeff, cov = np.polyfit(xs, ys, 1, w=weights, rcond=rcond, cov = True)
        if error:
            return coeff[1], np.sqrt(cov[1, 1])
        return coeff[1]

