OPENQASM 3;

input uint[4] a_in;
input uint[4] b_in;

gate majority a, b, c {
    ctrl @ x c, b;
    ctrl @ x c, a;
    ctrl(2) @ x a, b, c;
}

gate unmaj a, b, c {
    ccnot a, b, c;
    cnot c, a;
    cnot a, b;
}

qubit cin;
qubit[4] a;
qubit[4] b;
qubit cout;

// set input states
for int[8] i in [0: 3] {
  if(bool(a_in[i])) x a[i];
  if(bool(b_in[i])) x b[i];
}

// add a to b, storing result in b
majority cin, b[3], a[3];
for int[8] i in [3: -1: 1] { majority a[i], b[i - 1], a[i - 1]; }
cnot a[0], cout;
for int[8] i in [1: 3] { unmaj a[i], b[i - 1], a[i - 1]; }
unmaj cin, b[3], a[3];

#pragma braket result probability cout
#pragma braket result probability b