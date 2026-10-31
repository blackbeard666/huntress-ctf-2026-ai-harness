import json,sys
A=json.load(open(sys.argv[1])); B=json.load(open(sys.argv[2]))
print(len(A),len(B))
n=min(len(A),len(B))
diff=[i for i in range(n) if A[i][0]!=B[i][0]]
print('ndiff',len(diff),diff[:20])
print('exp same', all(A[i][1:]==B[i][1:] for i in range(n)))
