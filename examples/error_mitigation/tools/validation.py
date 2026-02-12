import matplotlib.pyplot as plt
import numpy as np
from stat_tools import (
    perform_regression,
    perform_regression_ols,
)

"""
Here we validate that our regression procedure works well across a variety of EVs. 
"""

num_ys = 50
xs = np.array([1,2,3,4])
true_y0 = np.linspace(-1,1,num_ys)
decay = 0.9
# Generate x values
errors = 0.01*np.array([1,1,1/np.sqrt(2),1/2])

data = np.zeros((num_ys,len(xs)))
estimates = []
estimates_ols = []

for i in range(num_ys):
    for j in range(len(xs)):
        data[i,j] = true_y0[i] * np.exp(-decay*xs[j])
        data[i,j]+= np.random.normal(0, errors[j])
    errs = np.multiply(1/np.sqrt(np.abs(data[i,:])),errors)
    estimates.append(perform_regression(xs,data[i,:],variances=errors**2)[0])
    estimates_ols.append(perform_regression_ols(xs,data[i,:],variances=errors**2)[0])

# Estimate variances from noise

# Perform regression with and without variance weighting
labels = ['exp_v1', 'lin']
ests = [estimates, estimates_ols,]
for est, lab in zip(ests, labels):
    print(f"{lab}: {1/num_ys*np.sum(np.square(np.array(est)-true_y0))}")        

fig, ax = plt.subplots(1,1)
ax.scatter(true_y0, estimates, c = 'b', marker='x', label="exp")
ax.scatter(true_y0, estimates_ols, c='r', label='lin')
ax.plot([-1,1],[-1,1],c='k')
plt.legend()
plt.show()

