exec(open('fit.py').read().split("tapsets=")[0])
import itertools
tapsets=[(3,8,14,16)]+[tuple(sorted(x)) for x in itertools.combinations(range(1,17),4) if 16 in x]
# stage 1: no chx
for brot in (30,2,31,29,1,28):
  for arot in (5,27,4,6,3,7):
    for wrot in (1,31,2,0):
      for taps in tapsets:
          kw=dict(taps=taps,brot=brot,arot=arot,wrot=wrot)
          if ok(kw): print('FOUND',kw); sys.exit()
# stage 2: std taps one f change
for brot in (30,2):
  for taps in [(3,8,14,16),(3,9,14,16)]:
    for i in range(80):
      for j in range(4):
        if j==i//20: continue
        kw=dict(taps=taps,brot=brot,chx={i:j})
        if ok(kw): print('FOUND',kw); sys.exit()
print('none')
