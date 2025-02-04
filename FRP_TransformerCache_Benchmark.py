import torch
import time
import numpy as np
from collections import deque, Counter

# === CONFIGURATION ===
SEQ_LEN = 1024  
HEAD_DIM = 64  
NUM_HEADS = 12  
CACHE_SIZE = 2028  
NUM_ITERS = 10000  
FRP_P = 2029  

# === DETECT AMD ROCm GPU ===
device = torch.device("hip" if torch.cuda.is_available() else "cpu")

# === RANDOM KEY-VALUE PAIRS (SIMULATING TRANSFORMER CACHE) ===
def generate_kv_pairs(batch_size=1):
    """Simulate Transformer key-value pairs stored in ROCm GPU memory"""
    return torch.randn(batch_size, NUM_HEADS, HEAD_DIM, device=device)

# === FIFO CACHE ===
class FIFOCache:
    def __init__(self, max_size):
        self.cache = deque(maxlen=max_size)
        self.access_count = Counter()

    def access(self, kv):
        idx = len(self.cache) % CACHE_SIZE  # Simulating indexed access
        self.access_count[idx] += 1
        if len(self.cache) >= self.cache.maxlen:
            self.cache.popleft()  # Evict oldest entry
        self.cache.append(kv)

# === LRU CACHE ===
class LRUCache:
    def __init__(self, max_size):
        self.cache = {}
        self.order = deque()
        self.access_count = Counter()

    def access(self, key, kv):
        self.access_count[key % CACHE_SIZE] += 1
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= CACHE_SIZE:
            oldest_key = self.order.popleft()
            del self.cache[oldest_key]  
        self.cache[key] = kv
        self.order.append(key)

# === FRP CYCLIC SCHEDULING CACHE WITH TRACKING ===
class FRPCache:
    def __init__(self, max_size, prime_p):
        self.cache = [None] * max_size
        self.schedule = self.generate_optimized_frp_schedule(prime_p, max_size)
        self.index = 0
        self.access_count = Counter()
        self.collisions = 0

    def get_cyclic_sequence(self, p, max_digits=None):
        remainder = 1
        seen = {}
        sequence = ""
        remainder_order = []
        
        while remainder and remainder not in seen and (max_digits is None or len(sequence) < max_digits):
            seen[remainder] = len(sequence)
            remainder_order.append(remainder)
            remainder *= 10
            sequence += str(remainder // p)
            remainder %= p

        if remainder and max_digits is None:
            start = seen[remainder]
            sequence = sequence[start:]
            remainder_order = remainder_order[start:]

        return sequence, remainder_order

    def generate_optimized_frp_schedule(self, p, max_size):
        cyclic_sequence, _ = self.get_cyclic_sequence(p, max_size)
        d = len(str(p))  
        groups = self.generate_cyclic_groups(cyclic_sequence, d)

        if len(groups) < p - 1:
            raise ValueError(f"Insufficient cyclic groups: {len(groups)} < {p-1}")

        group_map = {}
        for idx, group in enumerate(groups):
            if group not in group_map:
                group_map[group] = idx

        schedule = []
        for n in range(1, p):
            idx = (n * (p - 1) // p) % (p - 1)
            if idx >= len(groups):
                idx = idx % len(groups)  
            schedule.append(group_map[groups[idx]])

        schedule = np.array(schedule[:max_size], dtype=int) % max_size
        return schedule

    def generate_cyclic_groups(self, sequence, group_size):
        n = len(sequence)
        groups = []
        for i in range(n):
            if i + group_size <= n:
                groups.append(sequence[i:i+group_size])
            else:
                wrap = sequence[i:] + sequence[:(i+group_size) % n]
                groups.append(wrap)
        
        return groups[:len(sequence)]

    def access(self, kv):
        idx = self.schedule[self.index]
        self.access_count[idx] += 1
        
        # Check for collision (if slot was previously filled)
        if self.cache[idx] is not None:
            self.collisions += 1  

        self.cache[idx] = kv
        self.index = (self.index + 1) % len(self.schedule)

# === BENCHMARK FUNCTION WITH METRICS ===
def benchmark_cache(cache_type, cache_obj):
    start_time = time.time()

    for i in range(NUM_ITERS):
        kv = generate_kv_pairs()
        if isinstance(cache_obj, LRUCache):
            cache_obj.access(i, kv)
        else:
            cache_obj.access(kv)

    elapsed_time = time.time() - start_time
    memory_utilization = sum(1 for x in cache_obj.cache if x is not None) / CACHE_SIZE
    avg_latency = elapsed_time / NUM_ITERS
    access_distribution = cache_obj.access_count

    if isinstance(cache_obj, FRPCache):
        collisions = cache_obj.collisions
    else:
        collisions = None  

    return elapsed_time, avg_latency, memory_utilization, access_distribution, collisions

# === RUN BENCHMARKS ===
fifo_cache = FIFOCache(CACHE_SIZE)
lru_cache = LRUCache(CACHE_SIZE)
frp_cache = FRPCache(CACHE_SIZE, FRP_P)

results = {
    "FIFO": benchmark_cache("FIFO", fifo_cache),
    "LRU": benchmark_cache("LRU", lru_cache),
    "FRP": benchmark_cache("FRP", frp_cache),
}

# === DISPLAY RESULTS WITH ACCESS ANALYSIS ===
print("\n==== BENCHMARK RESULTS (ROCm AMD) ====")
for method, (total_time, avg_latency, mem_util, access_distribution, collisions) in results.items():
    print(f"\n[{method}]:")
    print(f"  ➤ Total Time: {total_time:.4f}s")
    print(f"  ➤ Avg Access Latency: {avg_latency:.6f}s")
    print(f"  ➤ Memory Utilization: {mem_util:.2%}")
    
    if collisions is not None:
        print(f"  ➤ Collisions Detected: {collisions:,}")
    
    # Print access distribution sample (first 10 indices)
    sample_access = list(access_distribution.items())[:10]
    print(f"  ➤ Access Distribution (sample): {sample_access}")
