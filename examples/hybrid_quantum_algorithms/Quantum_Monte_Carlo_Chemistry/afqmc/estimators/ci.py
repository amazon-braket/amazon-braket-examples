# This file conducts the calculations using Slater-Condon rule, assuming a RHF starting point.
# Functions defined in this file is adapted from: github.com/pauxy-qmc/pauxy.
import numpy as np
import scipy.sparse.linalg


def get_hmatel(h1e, eri, di, dj):
    '''This function computes the matrix element <di|H|dj>. The Hamiltonian contains
    one-body and two-body terms, i.e., h1e and eri.
    Arg:
        h1e (np.ndarray): one-body operator in spatial-orbital basis
        eri (np.ndarray): two-body operator in modified physicist's notation
        di, dj (np.array): slater determinant
    '''
    from_orb = list(set(dj)-set(di))
    to_orb = list(set(di)-set(dj))
    from_orb.sort()
    to_orb.sort()
    nex = len(from_orb)
    perm = get_perm(from_orb, to_orb, di, dj)
    
    if nex == 0:
        hmatel, e1b, e2b = slater_condon0(h1e, eri, di)
    elif nex == 1:
        i, si = map_orb(from_orb[0])
        a, sa = map_orb(to_orb[0])
        hmatel, e1b, e2b = slater_condon1(h1e, eri, (i,si), (a,sa), di, perm)
    elif nex == 2:
        # < ij | ab > or < ij | ba >
        i, si = map_orb(from_orb[0])
        j, sj = map_orb(from_orb[1])
        a, sa = map_orb(to_orb[0])
        b, sb = map_orb(to_orb[1])
        hmatel = slater_condon2(eri, (i,si), (j,sj), (a,sa), (b,sb), perm)
        e1b = 0
        e2b = hmatel
    else:
        hmatel = 0.0
        e1b = 0.0
        e2b = 0.0
    return np.array([hmatel, e1b, e2b])


def get_perm(from_orb, to_orb, di, dj):
    """Determine sign of permutation needed to align two determinants.
    """
    nmove = 0
    perm = 0
    for o in from_orb:
        io = np.where(dj==o)[0]
        perm += io - nmove
        nmove += 1
    nmove = 0
    for o in to_orb:
        io = np.where(di==o)[0]
        perm += io - nmove
        nmove += 1
    return perm % 2 == 1


def slater_condon0(h1e, eri, occs):
    """This function computes <dj|H|dj>."""
    e2b = 0.0
    #e1b = prop.nuclear_repulsion
    e1b = 0.0
    for i in range(len(occs)):
        ii, spin_ii = map_orb(occs[i])
        # Todo: Update if H1 is ever spin dependent.
        e1b += h1e[ii,ii]
        
        for j in range(i+1,len(occs)):
            # <ij|ij> - <ij|ji>  # physicist's notation
            jj, spin_jj = map_orb(occs[j])
            # coulomb
            e2b += eri[ii,jj,jj,ii] # modified physicist's notation
            # exchange
            if spin_ii == spin_jj:
                e2b -= eri[ii,jj,ii,jj]
                
    hmatel = e1b + e2b
    return hmatel, e1b, e2b


def slater_condon1(h1e, eri, i, a, occs, perm):
    """This function computes <di|H|dj>, where di, dj differs by 1 orbital."""
    ii, si = i
    aa, sa = a
    e1b = h1e[aa, ii]
    nel = len(occs)
    e2b = 0
    for j in range(nel):
        # \sum_j <ij|aj> - <ij|ja> # physicist's notation
        oj = occs[j]
        oj, soj = map_orb(oj)
        if 2*oj+soj != 2*ii+si:
            e2b += eri[aa,oj,oj,ii] # modified into new notation and flip aa and ii
            if soj == si:
                e2b -= eri[aa,oj,ii,oj] # m
    hmatel = e1b + e2b
    if perm:
        return -hmatel, -e1b, -e2b
    else:
        return hmatel, e1b, e2b

    
def slater_condon2(eri, i, j, a, b, perm):
    """This function computes <di|H|dj>, where di, dj differs by 2 orbital."""
    ii, si = i
    jj, sj = j
    aa, sa = a
    bb, sb = b
    hmatel = 0.0
    if si == sa:
        hmatel = eri[aa,bb,jj,ii] # m
    if si == sb:
        hmatel -= eri[aa,bb,ii,jj] # m
    if perm:
        return -hmatel
    else:
        return hmatel


def map_orb(orb):
    """Map spin orbital to spatial index."""
    if orb % 2 == 0:
        s = 0
        ix = orb // 2
    else:
        s = 1
        ix = (orb - 1) // 2
    return ix, s


def get_one_body_matel(one_body, di, dj):
    """The one-body operator has to be the same dimension as spatial basis."""
    from_orb = list(set(dj)-set(di))
    to_orb = list(set(di)-set(dj))
    nex = len(from_orb)
    perm = get_perm(from_orb, to_orb, di, dj)
    matel = 0.0
    if nex == 0:
        for i in range(len(di)):
            ii, spin_ii = map_orb(di[i])
            matel += one_body[ii, ii]
    elif nex == 1:
        i, si = map_orb(from_orb[0])
        a, sa = map_orb(to_orb[0])
        assert si == sa
        matel = one_body[a, i]
    else:
        matel = 0.0
    if perm:
        return -matel
    else:
        return matel