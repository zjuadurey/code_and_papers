def maxcut_bruteforce(adj):
    n=len(adj)
    best=-1
    best_part=None
    for mask in range(1<<n):
        left=[i for i in range(n) if (mask>>i)&1]
        right=[i for i in range(n) if not (mask>>i)&1]
        val=0
        for i in range(n):
            for j in range(i+1,n):
                if adj[i][j]!=0 and ((i in left and j in right) or (i in right and j in left)):
                    val+=adj[i][j]
        if val>best:
            best=val
            best_part=(left,right)
    return best,best_part
