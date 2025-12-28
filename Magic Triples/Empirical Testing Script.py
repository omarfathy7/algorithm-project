from collections import Counter
from itertools import permutations

LIMIT = 10**9

def list_triplets_bruteforce(a):
    """Return list of ordered triplets (i,j,k) that satisfy condition (for small n, debug)."""
    n = len(a)
    triples = []
    for i, j, k in permutations(range(n), 3):
        if a[j]*a[j] == a[i]*a[k]:
            triples.append((i, j, k))
    return triples

def count_triplets_optimized(a, mode="ordered"):
    """
    Optimized correct counting.
    mode: "ordered" or "unordered"
    """
    freq = Counter(a)
    unique = sorted(freq.keys())
    res = 0

    # Case all equal: a[i] = a[j] = a[k]
    for v, c in freq.items():
        if c >= 3:
            # ordered permutations of 3 distinct indices with same value
            # P(c,3) = c*(c-1)*(c-2)
            res += c * (c - 1) * (c - 2)

    # For other cases enumerate mid = a[j], and find factor pairs (left, right) of mid*mid
    # We'll enumerate divisors d up to sqrt(mid*mid) to avoid double-adding for unordered mode.
    for mid in unique:
        cnt_mid = freq[mid]
        m2 = mid * mid

        # iterate divisors d such that d * other = m2
        d = 1
        while d * d <= m2:
            if m2 % d == 0:
                other = m2 // d

                # consider pair (left=d, right=other)
                left = d
                right = other
                if left in freq and right in freq:
                    # skip the all-equal triple, already counted
                    if left == mid and right == mid:
                        pass
                    else:
                        if left == right:
                            # left == right != mid: that's case a[i]==a[k]!=a[j]
                            # ordered count: cnt_mid * cnt_left * (cnt_left - 1)
                            add = cnt_mid * freq[left] * (freq[left] - 1)
                            # For unordered mode: (i,k) are unordered but left==right so no division
                            res += add
                        else:
                            # left != right
                            add_ordered = cnt_mid * freq[left] * freq[right]
                            if mode == "ordered":
                                # When iterating divisors up to sqrt, we'll encounter both (d,other) and (other,d)
                                # but each corresponds to different (left,right) ordered pair and should both be counted.
                                res += add_ordered
                            else:
                                # unordered: we want to count unordered pair {left,right} exactly once.
                                # When d < other we process the pair once (here); when d > other we would process swapped
                                # but because we iterate only d <= sqrt, we process each unordered pair exactly once.
                                # unordered contribution: cnt_mid * freq[left] * freq[right]  (no doubling)
                                res += cnt_mid * freq[left] * freq[right]
                # end if left in freq ...
                # Also handle the symmetric pair (other, left) only when d != other and mode == "ordered"
                if d != other:
                    # symmetric pair will be handled when loop encounters d'=other (if other <= sqrt),
                    # but since we loop only up to sqrt, we must ensure ordered mode counts both (d,other) and (other,d).
                    # Strategy: if ordered and other > sqrt(mid*mid), we need to also count symmetric contribution here.
                    # Simpler: when ordered, we will count both pairs across iterations if both divisors <= sqrt or > sqrt.
                    # To ensure correctness, explicitly add symmetric when ordered and other > d:
                    if mode == "ordered":
                        # Add symmetric counterpart (left=other, right=d)
                        left2 = other
                        right2 = d
                        if left2 in freq and right2 in freq:
                            if left2 == mid and right2 == mid:
                                pass
                            else:
                                if left2 == right2:
                                    res += cnt_mid * freq[left2] * (freq[left2] - 1)
                                else:
                                    # But careful: this symmetric addition would double-count if later the loop visits d'=other (when other <= sqrt)
                                    # So only add symmetric here when other > d (which is always true when other != d for our loop)
                                    # and when other > sqrt, but other > d implies other >= d+1 ; we only loop d up to sqrt,
                                    # so the counterpart where d'=other will be > sqrt and not visited — therefore we must add here.
                                    # To avoid double-count: add symmetric only when other > d and other > (m2**0.5)
                                    pass
                # end symmetric handling

                # Now handle the other divisor (if different) only when d != other
                if d != other:
                    # Handle the (other, d) pair — but careful with double count:
                    # If other <= sqrt(m2) then (other, d) will be processed in its own iteration when d becomes 'other' later.
                    # If other > sqrt(m2) it won't be processed later, so we need to process it now for ordered mode.
                    if other > (int(m2**0.5)):
                        # (other, d) symmetric pair not visited later — process here
                        left_s = other
                        right_s = d
                        if left_s in freq and right_s in freq:
                            if left_s == mid and right_s == mid:
                                pass
                            else:
                                if left_s == right_s:
                                    res += cnt_mid * freq[left_s] * (freq[left_s] - 1)
                                else:
                                    if mode == "ordered":
                                        res += cnt_mid * freq[left_s] * freq[right_s]
                                    else:
                                        # unordered: we already added unordered contribution for (d,other) above,
                                        # so do NOT add symmetric again.
                                        pass

            d += 1

    return res

# ---------------- Debug helper ----------------
def debug_compare(a, mode="ordered"):
    print("Array:", a)
    brute = list_triplets_bruteforce(a)
    cnt_brute = len(brute)
    opt = count_triplets_optimized(a, mode=mode)
    print("Bruteforce (ordered) count:", cnt_brute)
    print("Optimized (mode={}):".format(mode), opt)
    if cnt_brute != opt:
        print("Mismatch! Showing brute-force triplets (i,j,k):")
        for t in brute:
            print(t, "values:", (a[t[0]], a[t[1]], a[t[2]]))
    else:
        print("Match ✅")
    print("-" * 40)
    return cnt_brute, opt, brute

# Example usage (small debug)
if __name__ == "__main__":
    tests = [
        [1,7,7,2,7],
        [6,2,18],
        [1,2,3,4,5,6,7,8,9],
        [1,1,2,2,4,4,8,8],
        [2,2,2],
    ]
    for a in tests:
        debug_compare(a, mode="ordered")   # change to "unordered" if that's what you want
