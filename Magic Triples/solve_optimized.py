from collections import Counter

LIMIT = 10**9

def solve_optimized():
    n = int(input())
    a = list(map(int, input().split()))
    
    freq = Counter(a)
    unique_vals = list(freq.keys())
    
    ret = 0
    
    # Case b=1: same value appears ≥3 times
    for val, c in freq.items():
        if c >= 3:
            ret += c * (c - 1) * (c - 2)
    
    # Case b≥2: geometric progression
    for val in unique_vals:
        cnt_val = freq[val]
        
        if val >= 1_000_000:
            max_b = LIMIT // val
            for b in range(2, max_b + 1):
                if val % b == 0:
                    left = val // b
                    right = val * b
                    if left in freq and right in freq:
                        ret += cnt_val * freq[left] * freq[right]
        else:
            divisor = 1
            while divisor * divisor <= val:
                if val % divisor == 0:
                    # divisor as b
                    if divisor > 1:
                        left = val // divisor
                        right = val * divisor
                        if left in freq and right in freq:
                            ret += cnt_val * freq[left] * freq[right]
                    
                    # other factor
                    other = val // divisor
                    if other != divisor and other > 1:
                        left = divisor
                        right = val * other
                        if left in freq and right in freq:
                            ret += cnt_val * freq[left] * freq[right]
                divisor += 1
    
    print(ret)

def main_optimized():
    t = int(input())
    for _ in range(t):
        solve_optimized()

if __name__ == "__main__":
    main_optimized()
