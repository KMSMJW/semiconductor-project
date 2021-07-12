from docplex.mp.model import Model
from docplex.mp.advmodel import AdvModel as Model
from collections import namedtuple
from docplex.util.environment import get_environment
import cplex
import docplex
import pandas as pd
import random
import types
# from test23 import availsize
from test23 import work
from test23 import pkg_step
from test23 import fab_step
from test23 import pkg_line_step
from test23 import fab_line_step
from test23 import simulation
from test23 import simu
from simulation import availsize
from simulation import amount
from simulation import consume
from simulation import pkg_process
from simulation import fab_process
from simulation import step
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
dir(types)

# index
# Fab line i
Fab = 4

# wafer type j
wafer = 10

# EDS line k
EDS = 3

# PKG line l
PKG = 4

# product type p
product = 30

# time t
time = 18

# parameter
#PKG Capa
Capa_PKG_line = {}
df = pd.read_excel('기본 data.xlsx', sheet_name = 'PKG line 생산량 제약')
for l in range (0,PKG):
    Capa_PKG_line[l] = df.iloc[0,5*l+3]
Capa_PKG_wafer = {}
for l in range(0,PKG):
    for j in range(0,wafer):
        for t in range(0,time):
            Capa_PKG_wafer[(j,l)] = df.iloc[j,5*l+2]

#EDS Capa
Capa_EDS = {}
df1 = pd.read_excel('기본 data.xlsx', sheet_name = 'EDS line 생산량 제약')
for k in range(0,EDS):
    Capa_EDS[k] = df1.iloc[10*k ,3]

#Fab Capa
Capa_Fab_line = {}
df2 = pd.read_excel('기본 data.xlsx', sheet_name= 'Fab line 생산량 제약')
for i in range(0,Fab):
    Capa_Fab_line[i] = df2.iloc[10*i,3]
Capa_Fab_wafer = {}
for i in range(0,Fab):
    for j in range(0,wafer):
        Capa_Fab_wafer[(i,j)] = df2.iloc[10*i+j,2]

# ND
ND = {}
df8 = pd.read_excel('기본 data.xlsx', sheet_name='수율')
for j in range(0,wafer):
    for p in range(0,product):
        ND[(j,p)] = df8.iloc[p,1]

# t월의 일수
Days = {}
day = [31, 29, 31, 30, 31, 30, 30, 31, 30, 31, 30, 31]
for t in range(0,time):
    Days[t] = day[t%12]

# PKG line의 product 생산여부
LP = {}
df3 = pd.read_excel('기본 data.xlsx', sheet_name= 'PKG_line-Product 매칭')
for l in range(0,PKG):
    for p in range(0,product):
        LP[(l,p)] = df3.iloc[p+1, l+2]
JL = {}
for l in range(0,PKG):
    for j in range(0,wafer):
        JL[(j,l)] = df3.iloc[j+1, l+11]

# Fab line의 wafer 생산 여부
df6 = pd.read_excel('기본 data.xlsx', sheet_name='Fab_line-Wafer 매칭')
IJ = {}
for i in range(0,Fab):
    for j in range(0,wafer):
        IJ[(i,j)] = df6.iloc[j+1,i+2]

# PKG line의 초기 재공
PKG_inventory = {}
df9 = pd.read_excel('기본 data.xlsx', sheet_name= 'eoh_PKG')
for j in range(0,wafer):
    for l in range(0,PKG):
        if JL[(j,l)] == 1:
            PKG_inventory[(j,l)] = 125
        else:
            PKG_inventory[(j,l)] = 0

Fab_inventory = {}
for j in range(0,wafer):
    for i in range(0,Fab):
        if IJ[(i,j)] == 1:
            Fab_inventory[(i,j)] = 300
        else:
            Fab_inventory[(i,j)] = 0

avail_Fab_inventory = {}
for j in range(0,wafer):
    for i in range(0,Fab):
        if IJ[(i,j)] == 1:
            avail_Fab_inventory[(i,j)] = 150
        else:
            avail_Fab_inventory[(i,j)] = 0

non_avail_inventory = {}
for j in range(0,wafer):
    for i in range(0,Fab):
        if IJ[(i,j)] == 1:
            non_avail_inventory[(i,j)] = 150
        else:
            non_avail_inventory[(i,j)] = 0


# wafer의 product 공정 가능 여부
df4 = pd.read_excel('기본 data.xlsx', sheet_name='wafer-product 매칭')
JP = {}
for j in range(0,wafer):
    for p in range(0, product):
        JP[(j,p)] = df4.iloc[p+1, j+2]

# EDS line의 wafer 공정 여부
df5 = pd.read_excel('기본 data.xlsx', sheet_name='EDS_line-Wafer 매칭')
KJ = {}
for k in range(0,EDS):
    for j in range(0,wafer):
        KJ[(k,j)] = df5.iloc[j+1, k+2]
g=8
#생산 목표
df7 = pd.read_excel('newtarget.xlsx', sheet_name='%d'%g)
Target = {}
for j in range(0,wafer):
    for t in range(0,time):
        Target[(j,t)] = df7.iloc[j+1,t%12+2]

in_cap = {}
for i in range(0,Fab):
    for j in range(0,wafer):
        if IJ[i,j] == 1:
            in_cap[(i,j)] = 10000
        else:
            in_cap[(i,j)] = 0

# 모델 구성
def samsung_model(**kwargs):
    mdl = Model(name='good', **kwargs)

    # 결정 변수
    # Fab line 별 투입 wafer 양
    x_in = mdl.continuous_var_cube(keys1 = Fab, keys2= wafer, keys3 = time, name= 'x_in')
    mdl.x_in = x_in

    #Fab 에서 출고한 wafer 양
    x_out = mdl.continuous_var_cube(keys1= Fab, keys2= wafer, keys3= time, name= 'x_out')
    mdl.x_out = x_out

    #EDS에서 처리한 wafer 양
    y = mdl.continuous_var_cube(keys1= EDS, keys2= wafer, keys3= time, name ='y')
    mdl.y = y

    #PKG line에 투입되는 wafer 양
    z_in = mdl.continuous_var_cube(keys1= wafer, keys2= PKG, keys3 = time, name='z_in')
    mdl.z_in = z_in

    #PKG line에서 출고한 product의 양
    z_out = mdl.continuous_var_cube(keys1= wafer, keys2 = PKG, keys3 = time, name= 'z_out')
    mdl.z_out = z_out

    k = mdl.continuous_var_cube(keys1= Fab, keys2=wafer, keys3=time, name='k')
    mdl.k = k

    non_avail = mdl.continuous_var_cube(keys1=Fab, keys2=wafer, keys3=time, name='non_avail')
    mdl.non_avail = non_avail

    alpha_avail = mdl.continuous_var_matrix(keys1=Fab, keys2= time, name = 'alpha_avail')
    mdl.alpha_avail = alpha_avail

    alpha_nonavail = mdl.continuous_var_matrix(keys1=Fab, keys2=time, name='alpha_nonaavail')
    mdl.alpha_nonavail = alpha_nonavail

    alpha_PKG = mdl.continuous_var_matrix(keys1=PKG, keys2= time, name= 'alpha_PKG')
    mdl.alpha_PKG = alpha_PKG

    #Fab line 재공
    eoh_Fab = mdl.continuous_var_cube(keys1 = Fab, keys2 = wafer, keys3= time, name='eoh_Fab')
    mdl.eoh_Fab = eoh_Fab

    #PKG line 재공
    eoh_PKG = mdl.continuous_var_cube(keys1= wafer, keys2= PKG, keys3 = time, name='eoh_PKG')
    mdl.eoh_PKG = eoh_PKG

    #Fab line 출고가능 수량
    avail_Fab = mdl.continuous_var_cube(keys1= Fab, keys2= wafer, keys3= time, name='avail_Fab')
    mdl.avail_Fab = avail_Fab

    #PKG line 출고 가능 수량
    avail_PKG = mdl.continuous_var_cube(keys1= wafer, keys2= PKG, keys3 = time, name= 'avail_PKG')
    mdl.avail_PKG = avail_PKG

    #제품 최종 생산량
    Product = mdl.continuous_var_matrix(keys1= wafer, keys2= time, name= 'Product')
    mdl.Product = Product

    #영업 요청 충족량, 미달량
    less_prod = mdl.continuous_var_matrix(keys1= wafer, keys2= time, lb=0, name='less_prod')
    over_prod = mdl.continuous_var_matrix(keys1= wafer, keys2= time, lb=0, name='over_prod')
    mdl.less_prod = less_prod
    mdl.over_prod = over_prod

    #완성 재고(B)
    B = mdl.continuous_var_matrix(keys1=wafer, keys2=time, name="B")
    mdl.B = B


    #제약 조건
    #0-1. buffer 수량 계산
    for j in range(0,wafer):
        for t in range(1,time):
            mdl.add_constraint(B[j,t] == mdl.sum(z_out[j,l,t] for l in range(0,PKG)) + B[j,t-1] - Product[j,t])

    for j in range(0,wafer):
        mdl.add_constraint(B[j,0] == mdl.sum(z_out[j,l,0] for l in range(0,PKG)) - Product[j,0])

    #0-2. buffer 용량
    for t in range(0,time):
        mdl.add_constraint(mdl.sum(B[j,t] for j in range(0,wafer)) <= 2000)

    #2. PKG line 생산량 제약
    for l in range(0,PKG):
        for t in range(0,time):
            mdl.add_constraint(mdl.sum(z_out[j,l,t] for j in range(0,wafer)) <= Capa_PKG_line[l])

    for l in range(0,PKG):
        for j in range(0,wafer):
            for t in range(0,time):
                mdl.add_constraint(z_out[j,l,t] <= Capa_PKG_wafer[j,l])

    #3. PKG line EOH 계산
    for j in range(0,wafer):
        for l in range(0,PKG):
            for t in range(1,time):
                mdl.add_constraint(eoh_PKG[j,l,t] == eoh_PKG[j,l,t-1] +z_in[j,l,t] - z_out[j,l,t])
    for j in range(0,wafer):
        for l in range(0,PKG):
            mdl.add_constraint(eoh_PKG[j,l,0] == PKG_inventory[j,l] - z_out[j,l,0] + z_in[j,l,0])

    #4. avail 계산
    for j in range(0,wafer):
        for l in range(0,PKG):
            for t in range(1,time):
                mdl.add_constraint(avail_PKG[j,l,t] == eoh_PKG[j,l,t-1] + z_in[j,l,t]*((Days[t]-25)/Days[t]))
    for j in range(0,wafer):
        for l in range(0,PKG):
            mdl.add_constraint(avail_PKG[j,l,0] == PKG_inventory[j,l] + z_in[j,l,0]*((31-25)/31))

    #5. PKG line 출고량 계산
    for l in range(0,PKG):
        for j in range(0,wafer):
            for t in range(0,time):
                mdl.add_constraint(z_out[j,l,t] <= avail_PKG[j,l,t])

    for j in range(0,wafer):
        for i in range(0,Fab):
            for t in range(1,time):
                mdl.add_constraint(eoh_Fab[i,j,t] == eoh_Fab[i,j,t-1] + x_in[i,j,t] - x_out[i,j,t])

    for j in range(0,wafer):
        for i in range(0,Fab):
            mdl.add_constraint(eoh_Fab[i,j,0] == Fab_inventory[i,j] + x_in[i,j,0] - x_out[i,j,0])

    #10. Buffer - Fab 연결
    for j in range(0,wafer):
        for t in range(0,time):
            mdl.add_constraint(mdl.sum(x_out[i,j,t] for i in range(0,Fab)) == mdl.sum(z_in[j,l,t] for l in range(0,PKG)))

    for i in range(0,Fab):
        for j in range(0,wafer):
            for t in range(0,time):
                mdl.add_constraint(x_in[i,j,t] <= in_cap[i,j])

    for i in range(0,Fab):
        for j in range(0,wafer):
            for t in range(1,time):
                mdl.add_constraint(avail_Fab[i,j,t] == 30*eoh_Fab[i,j,t-1]/60)
    for i in range(0,Fab):
        for j in range(0,wafer):
            mdl.add_constraint(avail_Fab[i,j,0] == 30*Fab_inventory[i,j]/60)

    #14. Fab line 출고량 제약
    for i in range(0,Fab):
        for j in range(0,wafer):
            for t in range(0,time):
                mdl.add_constraint(x_out[i,j,t] <= avail_Fab[i,j,t])

    #15. Fab line 생산량 제약
    for i in range(0,Fab):
        for t in range(0,time):
            mdl.add_constraint(mdl.sum(x_out[i,j,t] for j in range(0,wafer)) <= Capa_Fab_line[i])

    for i in range(0,Fab):
        for t in range(0,time):
            for j in range(0,wafer):
                mdl.add_constraint(x_out[i,j,t] <= Capa_Fab_wafer[i,j])

    # 11. control 제약식
    # for i in range(0,Fab):
    #     for t in range(3,time):
    #         mdl.add_constraint(mdl.sum(eoh_Fab[i,j,t] for j in range(0,wafer)) <= 800*60*1.1/30)
    # for i in range(0,Fab):
    #     for t in range(3,time):
    #         mdl.add_constraint(800*60*0.9/30 <= mdl.sum(eoh_Fab[i,j,t] for j in range(0,wafer)))
    #
    # for l in range(0,PKG):
    #     for t in range(3,time):
    #         mdl.add_constraint(mdl.sum(eoh_PKG[j,l,t] for j in range(0,wafer)) <= 800*25*1.1/30)
    # for l in range(0,PKG):
    #     for t in range(3,time):
    #         mdl.add_constraint(800*25*0.9/30 <= mdl.sum(eoh_PKG[j,l,t] for j in range(0,wafer)))


    for t in range(0,time):
        for j in range(0,wafer):
            mdl.add_constraint(Target[j,t] - Product[j,t] == less_prod[j,t] - over_prod[j,t])

    mdl.minimize(mdl.sum(mdl.sum(less_prod[j,t] for j in range(0,wafer)) for t in range(0,time)))

    return mdl

def clearing_PKG(l,t):
    wip = sum(mdl.eoh_PKG[j,l,t].solution_value for j in range(0,wafer))
    clear = 0
    for o in range(t,time):
        clear = clear + min(wip/sum(mdl.z_out[j,l,o].solution_value for j in range(0,wafer)),1)
        wip = max(wip - sum(mdl.z_out[j,l,o].solution_value for j in range(0,wafer)),0)
    return clear

def clearing_Fab(i,j,t):
    wip = mdl.eoh_Fab[i,j,t].solution_value
    clear = 0
    for o in range(t,time):
        clear = clear + min(wip/(mdl.x_out[i,j,o].solution_value+1),1)
        wip = max(wip - mdl.x_out[i,j,o].solution_value,0)
    return clear

def little(l,t):
    value = max(sum(mdl.eoh_PKG[j,l,t].solution_value for j in range(0,wafer))/sum(mdl.z_out[j,l,t].solution_value for j in range(0,wafer)),0)
    return value
input_check = []
result = []
for g in range(0,60):
# 생산 목표
    df7 = pd.read_excel('target60.xlsx', sheet_name='target')
    Target = {}
    for j in range(0,wafer):
        for t in range(0,time):
            Target[(j,t)] = df7.iloc[g,4+j+t%12*10]
    TAT = 25
    if __name__ == '__main__':
        mdl = samsung_model()
        if mdl.solve():
            input = []
            for t in range(0,time):
                for k in range(0,6):
                    line_input = []
                    for i in range(0,Fab):
                        line = []
                        for j in range(0,wafer):
                            if IJ[i,j] == 1:
                                line.append(mdl.x_in[i,j,t].solution_value/6)
                        line_input.append(line)
                    input.append(line_input)
            FAB_origin = [[[[1,25], [2,25], [3,25], [4,25], [5,25], [6,25], [7,25], [8,25], [9,25], [10,25],
                            [11,25], [[12,25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]]], [[[1,25], [2,25], [3,25], [4,25], [5,25], [6,25], [7,25], [8,25], [9,25], [10,25],
                            [11,25], [[12,25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]]], [[[1,25], [2,25], [3,25], [4,25], [5,25], [6,25], [7,25], [8,25], [9,25], [10,25],
                            [11,25], [[12,25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]]], [[[1,25], [2,25], [3,25], [4,25], [5,25], [6,25], [7,25], [8,25], [9,25], [10,25],
                            [11,25], [[12,25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]],
                           [[1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25],
                            [11, 25], [[12, 25]]]]]
            PKG_origin = [
                [[[1,25], [2,25], [3,25], [4,25], [[5,25]]], [[1,25], [2,25], [3,25], [4,25], [[5,25]]],
                 [[1,25], [2,25], [3,25], [4,25], [[5,25]]], [[1,25], [2,25], [3,25], [4,25], [[5,25]]],
                 [[1,25], [2,25], [3,25], [4,25], [[5,25]]]],
                [[[1,25], [2,25], [3,25], [4,25], [[5,25]]], [[1,25], [2,25], [3,25], [4,25], [[5,25]]],
                 [[1,25], [2,25], [3,25], [4,25], [[5,25]]], [[1,25], [2,25], [3,25], [4,25], [[5,25]]],
                 [[1,25], [2,25], [3,25], [4,25], [[5,25]]]],
                [[[1,25], [2,25], [3,25], [4,25], [[5,25]]], [[1,25], [2,25], [3,25], [4,25], [[5,25]]],
                 [[1,25], [2,25], [3,25], [4,25], [[5,25]]], [[1,25], [2,25], [3,25], [4,25], [[5,25]]],
                 [[1,25], [2,25], [3,25], [4,25], [[5,25]]]],
                [[[1,25], [2,25], [3,25], [4,25], [[5,25]]], [[1,25], [2,25], [3,25], [4,25], [[5,25]]],
                 [[1,25], [2,25], [3,25], [4,25], [[5,25]]], [[1,25], [2,25], [3,25], [4,25], [[5,25]]],
                 [[1,25], [2,25], [3,25], [4,25], [[5,25]]]]]
            rato = {}
            for t in range(0,time*6):
                for j in range(0,wafer):
                    for l in range(0,PKG):
                        k = t//6
                        if JL[j,l] == 1:
                            if sum(mdl.z_in[j,l,k].solution_value for l in range(0,PKG)) == 0:
                                rato[(j,l,t)] = 0.5
                            else:
                                rato[(j,l,t)] = mdl.z_in[j,l,k].solution_value/sum(mdl.z_in[j,l,k].solution_value for l in range(0,PKG))
            output = []
            output1 = []
            regression = []
            check = []
            fill = []
            regression1 = []
            for t in range(0,(time-6)*6):
                step(FAB_origin,PKG_origin,input[t],output,output1,t,rato,regression,regression1,check,fill)
                for k in input[t]:
                    input_check.append(sum(k))
            outlist = []
            eohlist = []
            for k in regression:
                outlist.append(k[0] * 6 / 800)
                eohlist.append([k[1]])
            line_fitter = LinearRegression()
            line_fitter.fit(eohlist, outlist)
            total_fab = 0
            for j in output:
                total_fab = total_fab + j[1]
            fab_tat = 0
            for j in output:
                fab_tat = fab_tat + j[0]*j[1]/total_fab

            total_pkg = 0
            for j in output1:
                total_pkg = total_pkg + j[1]
            pkg_tat = 0
            for j in output1:
                pkg_tat = pkg_tat + j[0] * j[1] / total_pkg

            fulfill = []
            for j in range(0, wafer):
                for t in range(0, 12):
                    fulfill.append(min(1, mdl.Product[j, t].solution_value / Target[j, t]))
            total_fulfill = sum(fulfill) / (10 * 12)

            inven = [0,0,0,0,0,0,0,0,0,0]
            satis = []
            for t in range(0,(time-6)*6):
                for j in range(0,10):
                    k = t//6
                    inven[j] = inven[j] + fill[t][j]
                    if inven[j] >= Target[j,k]/6:
                        satis.append(1)
                        inven[j] = inven[j] - Target[j,k]/6
                    else:
                        satis.append(6*inven[j]/Target[j,k])
                        inven[j] = 0
            result.append([g, fab_tat * 5 - 60, pkg_tat * 5 - 25, total_fulfill, sum(satis) / (10 * 12 * 6)])
result_columns = ['scenario', 'Fab', 'PKG', 'plan', 'implement']
df_result = pd.DataFrame(result, columns=result_columns)
df_result.to_excel("prop.xlsx", sheet_name='prop')
