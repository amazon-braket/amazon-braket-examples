from itertools import product, repeat

from braket.circuits import Circuit
from braket.circuits.observables import Sum
from braket.circuits.serialization import IRType
from braket.program_sets import CircuitBinding


def print_program_set(program_set, result=None):
    """Prints the program set and its result
    
    Args:
        program_set: ProgramSet
        result: ProgramSetQuantumTaskResult
    
    """
    if result is not None:
        assert len(program_set) == len(result), "program_set and result must have the same length"
        print_result = True
    else:
        result = repeat((None,))
        print_result = False
    
    for i, (program, program_result) in enumerate(zip(program_set, result)):
        if isinstance(program, Circuit):
            circuit = program
            input_sets = None
            observables = None
        elif isinstance(program, CircuitBinding):
            circuit = program.circuit
            input_sets = program.input_sets
            observables = program.observables
            
        if isinstance(observables, Sum):
            sum_observable = True
            observable_list = observables.summands
        else:
            sum_observable = False
            observable_list = observables
            
        
        print(f"circuit {i}")
        print(circuit)
        
        if not print_result:
            program_result = repeat((None,))
        for j, (execution_result, (input_set, observable)) in enumerate(
            zip(
                program_result,
                product(
                    input_sets.as_list() if input_sets else (None,), 
                    observable_list if observable_list else (None,),
                )
            )
        ):
            print(f"execution {j}") 
            if input_set:
                print("\tinput_set:", input_set)
            if observable is not None:
                print("\tobservable:", observable.to_ir(ir_type=IRType("OPENQASM")))
            if print_result: 
                print("\tresult: ", execution_result.counts, end='')
                if observable is not None:
                    print(", expectation:", execution_result.expectation, end='')
                print()
        if sum_observable:
            print("sum observable:", observables.to_ir(ir_type=IRType("OPENQASM")))
            if print_result:
                print("\tresult: expectation:", program_result.expectation(), end='')
            print()
        print('-'*80)
    print(f"Total executions: {program_set.total_executables}")
