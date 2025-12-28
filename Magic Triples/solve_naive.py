def solve_naive_unordered():
    n = int(input().strip())
    a = list(map(int, input().split()))
    count = 0
    for j in range(n):
        for i in range(n):
            if i == j:
                continue
            for k in range(i + 1, n):  # enforce i < k
                if k == j:
                    continue
                if a[j] * a[j] == a[i] * a[k]:
                    count += 1
    print(count)

if __name__ == "__main__":
    t = int(input().strip())
    for _ in range(t):
        solve_naive_unordered()
