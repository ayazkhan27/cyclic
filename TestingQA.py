import random
import numpy as np
from math import gcd
import matplotlib.pyplot as plt

########################################
# 1) Check if p is an FRP in base b (Simple Demo)
########################################

def is_full_reptend_prime(p, b=10):
    if p < 2:
        return False
    # naive prime check
    for x in range(2,int(p**0.5)+1):
        if p % x == 0:
            return False
    # gcd check
    if gcd(b,p)!=1:
        return False
    # order check
    remainder=1
    for k in range(1,p):
        remainder=(remainder*b)%p
        if remainder==1:
            return (k==(p-1))
    return False

########################################
# 2) FRP Beacon class
########################################

class FRPBeacon:
    def __init__(self, prime_p, base=10, offset=1):
        self.p = prime_p
        self.base=base
        self.remainder = offset % prime_p
        # assert is_full_reptend_prime(prime_p, base), \"p not FRP\"

    def next_val(self):
        self.remainder=(self.remainder*self.base)%self.p
        return self.remainder

########################################
# 3) Generate Test Vectors from FRP vs. Random
########################################

def generate_test_vectors_frp(frp_obj, n_vectors=200):
    # Each time: read remainder => map to 16-bit instruction
    # We'll do a simplistic map: remainder mod 65536 => instruction
    # or we can break remainder into fields. We'll do remainder mod 16^4
    # for demonstration. If p < 65536, we do a second iteration or repeat.
    # For simplicity, just remainder mod 65536.
    vectors=[]
    for i in range(n_vectors):
        r=frp_obj.next_val()
        instr = r % 65536  # map to 16-bit space
        vectors.append(instr)
    return vectors

def generate_test_vectors_random(n_vectors=200):
    vectors=[]
    for i in range(n_vectors):
        instr=random.randrange(65536)
        vectors.append(instr)
    return vectors

########################################
# 4) Coverage Metrics
########################################

def decode_instruction(instr):
    # 16-bit => fields:
    opcode = (instr>>12)&0xF
    regA   = (instr>>8)&0xF
    regB   = (instr>>4)&0xF
    imm4   = (instr>>0)&0xF
    return (opcode, regA, regB, imm4)

def coverage_report(instructions):
    # measure how many distinct (opcode, regA, regB, imm4)
    # how many distinct opcodes alone
    seen_opcodes=set()
    seen_regA=set()
    seen_regB=set()
    seen_imm4=set()
    seen_full=set()
    for instr in instructions:
        op,ra,rb,im=decode_instruction(instr)
        seen_opcodes.add(op)
        seen_regA.add(ra)
        seen_regB.add(rb)
        seen_imm4.add(im)
        seen_full.add((op,ra,rb,im))
    return {
        'distinct_opcodes': len(seen_opcodes),
        'distinct_regA': len(seen_regA),
        'distinct_regB': len(seen_regB),
        'distinct_imm4': len(seen_imm4),
        'distinct_full': len(seen_full)
    }

########################################
# 5) Demo / Benchmark
########################################

if __name__=='__main__':
    # Example: pick prime p=65537, base=10, assume it's FRP
    p=65537
    base=10
    is_frp=is_full_reptend_prime(p, base)
    print(f\"Prime={p}, base={base}, is_full_reptend? {is_frp}\")
    
    # Initialize FRP beacon
    beacon=FRPBeacon(p, base=base, offset=1)

    # We'll generate e.g. 200 test vectors from FRP
    frp_instrs=generate_test_vectors_frp(beacon, n_vectors=200)
    # We'll generate 200 from random
    rand_instrs=generate_test_vectors_random(n_vectors=200)

    # Evaluate coverage
    frp_cov=coverage_report(frp_instrs)
    rand_cov=coverage_report(rand_instrs)

    print(f\"FRP Coverage (200 vectors): {frp_cov}\")
    print(f\"Random Coverage (200 vectors): {rand_cov}\")

    # Possibly repeat with bigger sets
    bigger=1000
    beacon2=FRPBeacon(p, base=base, offset=1)
    frp_instrs2=generate_test_vectors_frp(beacon2, n_vectors=bigger)
    rand_instrs2=generate_test_vectors_random(n_vectors=bigger)
    frp_cov2=coverage_report(frp_instrs2)
    rand_cov2=coverage_report(rand_instrs2)

    print(f\"\\nFRP Coverage (1000 vectors): {frp_cov2}\")
    print(f\"Random Coverage (1000 vectors): {rand_cov2}\")
