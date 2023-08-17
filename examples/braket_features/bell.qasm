
OPENQASM 3;

qubit[2] q;
bit[2] c;

h q[0];
cnot q[0], q[1];

c = measure q;
