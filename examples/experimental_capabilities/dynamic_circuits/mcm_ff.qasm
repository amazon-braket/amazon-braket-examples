// mcm_ff.qasm
// perform mid circuit measurement and active qubit reset 
OPENQASM 3;
bit[1] c;
#pragma braket verbatim
box{
    prx(3.14, 0) $1;
    measure_ff(0) $1;
    cc_prx(3.14, 0, 0) $1;
    }
c[0] = measure $1;
