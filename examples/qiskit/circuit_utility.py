from braket.circuits import Circuit


def dprint(circuit : Circuit, max_width : int = 110) -> str:
    """Split Circuit string at logical column boundaries and depths for better display.
    
    Default appears to be 100-120, we take 110 conservatively. 
    """
    circuit_str = str(circuit)
    lines = circuit_str.strip().split('\n')
    if not lines or len(lines[0]) <= max_width:
        return print(circuit_str)
    # Find column positions from header row
    header = lines[0]
    cols = [i for i, c in enumerate(header) if c == '│']
    c0 = cols[0]
    breaks = [c0]
    i = 1
    while i < len(cols):
        if cols[i] - breaks[-1] > max_width - c0:
            breaks.append(cols[i-1])
        i+=1 
    breaks.append(cols[-1])
    result = []
    for i in range(len(breaks) - 1):
        start, end = breaks[i], breaks[i + 1]
        
        # Add section header for continuation
        if i > 0:
            result.append("")
        
        # Process each line for this section
        for line in lines:
            if len(line) <= start:
                continue
            
            section = line[0:c0] + line[start:end+1] 
            if end !=breaks[-1]:
                section += ' ||'
            result.append(section.rstrip())
    
    return print('\n'.join(result))
