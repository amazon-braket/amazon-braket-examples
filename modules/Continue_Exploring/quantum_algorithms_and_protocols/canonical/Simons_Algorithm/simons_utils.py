from braket.circuits import Circuit, circuit

@circuit.subroutine(register=True)
def simons_oracle(secret_s: str):
    """
    Quantum circuit implementing a particular oracle for Simon's problem. Details of this implementation are
    explained in the Simons Algorithm demo notebook.

    Args:
        secret_s (str): secret string we wish to find
    """
    # Find the index of the first 1 in s, to be used as the flag bit
    flag_bit=secret_s.find('1')
    
    n=len(secret_s)
    
    circ = Circuit()
    # First copy the first n qubits, so that |x>|0> -> |x>|x>
    for i in range(n):
        circ.cnot(i, i+n)
    
    # If flag_bit=-1, s is the all-zeros string, and we do nothing else.
    if flag_bit != -1:
        # Now apply the XOR with s whenever the flag bit is 1.
        for index,bit_value in enumerate(secret_s):
            
            if bit_value not in ['0','1']:
                raise Exception ('Incorrect char \'' + bit_value + '\' in secret string s:' + secret_s)
                
            # XOR with s whenever the flag bit is 1.
            # In terms of gates, XOR means we apply an X gate only whenever the corresponding bit in s is 1.
            # Applying this X only when the flag qubit is 1 means this is a CNOT gate.
            if(bit_value == '1'):
                circ.cnot(flag_bit,index+n)
    return circ
