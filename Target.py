#Target 엑셀 생성
import random
import pandas as pd
import types
gap= [0, 10, 25, 50]
ave = [280, 310, 340]
var = [5, 10, 15, 20, 25]
columns = ["average","gap","variability"]
for i in range(0,12):
    for j in range(0,10):
        columns.append("wafer%d"%(j+1))
target = []
for i in gap:
    for j in ave:
        for k in var:
            target1 = [j-i*2,j-i,j,j+i,j+i*2]*2
            targetlist = random.sample(target1,10)
            list = [j,i,k]
            for l in range(0,12):
                for h in targetlist:
                    list.append(round(h + (random.random()-0.5)*k))
            target.append(list)
df_target = pd.DataFrame(target,columns=columns)
df_target.to_excel("target_sample.xlsx",sheet_name = "target")