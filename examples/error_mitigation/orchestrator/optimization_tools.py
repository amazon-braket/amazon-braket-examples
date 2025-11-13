import random
import matplotlib.pyplot as plt
import numpy as np
from braket.quantum_information import PauliString


def greedy_coloring(pauli_observable : list[PauliString] | list[tuple[float,str]]):
    
    circuits = []
    if isinstance(pauli_observable[0], PauliString):
        pauli_observable = sorted(pauli_observable, key = lambda x : x.modulus)
    elif isinstance(pauli_observable[0], tuple):
        pauli_observable = sorted(pauli_observable, key = lambda x : x[0])
    
    for i in range(pauli_observable):
        # 
        # we would like to find a close match
        # (1) disjoint 
        pass

def max_norm_k_step(P, k):
    """L∞ norm k-step approximation using binary search."""
    n = len(P)
    
    # Calculate delta matrix
    delta = np.zeros((n, n))
    for j in range(n):
        for i in range(j):
            delta[i,j] = P[j] - P[i]
    
    def calculate_next(epsilon):
        i, j = 0, 0 
        array = []
        while i < n and j < n:
            if j == n-1 or delta[i,j+1] > epsilon:
                array.append(j+1)
                i += 1 
            else:
                j += 1 
        return array
    
    def decide(epsilon):
        i_s = [0]
        next_eps = calculate_next(epsilon)
        for j in range(k):
            i_s.append(next_eps[i_s[-1]])
            if i_s[-1] == n:
                return i_s
        return None
    
    # Binary search for optimal epsilon
    candidates = set()
    for i in range(n):
        for j in range(i+1, n):
            candidates.add((P[j] - P[i]) / 2)
    candidates = sorted(candidates)
    
    l, r = 0, len(candidates)
    while l < r:
        middle = (l + r) // 2
        if decide(candidates[middle]):
            r = middle
        else:
            l = middle + 1
    
    optimal_eps = candidates[l]
    boundaries = decide(optimal_eps)
    
    return boundaries, optimal_eps

def lp_norm_k_step(P, k, norm='L2', max_width=None, lambda_width=0.0):
    """Lp norm k-step approximation using dynamic programming."""
    n = len(P)
    
    if max_width:
        ideal_width = n / k
        if max_width < ideal_width:
            print(f'Warning: max_width={max_width} is less than ideal width {ideal_width:.1f}')
        if max_width > n:
            print(f'Warning: max_width={max_width} exceeds total points {n}')
    
    def segment_cost(segment, width):
        if norm == 'L2':
            step_val = np.mean(segment)
            error = np.sum((segment - step_val) ** 2)
        elif norm == 'L1':
            step_val = np.median(segment)
            error = np.sum(np.abs(segment - step_val))
        
        if max_width and width > max_width:
            error += lambda_width * (width - max_width) ** 2
        return error
    
    # Dynamic programming
    dp = np.full((n + 1, k + 1), np.inf)
    parent = np.full((n + 1, k + 1), -1, dtype=int)
    dp[0, 0] = 0
    
    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            for prev in range(j-1, i):
                width = i - prev
                cost = segment_cost(P[prev:i], width)
                if dp[prev, j-1] + cost < dp[i, j]:
                    dp[i, j] = dp[prev, j-1] + cost
                    parent[i, j] = prev
    
    optimal_cost = dp[n, k]
    
    # Reconstruct boundaries
    boundaries = []
    i, j = n, k
    while j > 0:
        boundaries.append(parent[i, j])
        i = parent[i, j]
        j -= 1
    boundaries = boundaries[::-1] + [n]
    
    return boundaries, optimal_cost

def plot_max_norm_fit(P, boundaries, k, optimal_eps):
    """Plot L∞ norm k-step fit."""
    n = len(P)
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(n)
    ax.scatter(x, P, label='Data points', s=50, zorder=3, color='blue')
    
    for idx in range(len(boundaries)-1):
        start, end = boundaries[idx], boundaries[idx+1]
        segment = P[start:end]
        step_val = (max(segment) + min(segment)) / 2
        error = (max(segment) - min(segment)) / 2
        
        ax.hlines(step_val, start-0.5, end-0.5, colors='red', linewidth=2, label='Step function' if idx == 0 else '')
        ax.fill_between([start-0.5, end-0.5], step_val-error, step_val+error, alpha=0.2, color='red')
    
    ax.set_xlabel('Index')
    ax.set_ylabel('Value')
    ax.set_title(f'L∞ Fit (k={k}, epsilon={optimal_eps:.6f})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.show()

def plot_lp_norm_fit(P, boundaries, k, norm, optimal_cost):
    """Plot Lp norm k-step fit."""
    n = len(P)
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(n)
    ax.scatter(x, P, label='Data points', s=50, zorder=3, color='blue')
    
    for idx in range(len(boundaries)-1):
        start, end = boundaries[idx], boundaries[idx+1]
        segment = P[start:end]
        if norm == 'L2':
            step_val = np.mean(segment)
        elif norm == 'L1':
            step_val = np.median(segment)
        ax.hlines(step_val, start-0.5, end-0.5, colors='red', linewidth=2, label='Step function' if idx == 0 else '')
    
    ax.set_xlabel('Index')
    ax.set_ylabel('Value')
    ax.set_title(f'{norm} Fit (k={k}, cost={optimal_cost:.6f})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    np.set_printoptions(precision=4, linewidth=400, suppress=True)

    random.seed(32)
    points = 100
    k = 3
    vals = [random.random()**3 for i in range(points)]
    t = sum(vals)
    vals = [k/t for k in sorted(vals, reverse=False)]
    vals = np.array(vals)

    boundaries, eps = max_norm_k_step(vals, k=4)
    plot_max_norm_fit(vals, boundaries, 4, eps)
    
    boundaries, cost = lp_norm_k_step(vals, k=4, norm='L2')
    plot_lp_norm_fit(vals, boundaries, 4, 'L2', cost)