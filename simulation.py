wafer1 = [[1,20],[2,25],[3,45],[4,25],[[5,20]]]
wafer2 = [[1,25],[2,30],[3,35],[4,25],[[5,30]]]
wafer3 = [[1,30],[2,15],[3,35],[4,35],[[5,40]]]
wafer4 = [[1,35],[2,45],[3,25],[4,45],[[5,30]]]
wafer5 = [[1,40],[2,35],[3,25],[4,55],[[5,20]]]
wafr1 = [[1,20],[2,20],[3,20],[4,20],[5,20],[6,20],[7,20],[8,20],[9,20],[10,20],[11,20],[[12,20]]]
wafr2 = [[1,20],[2,20],[3,20],[4,20],[5,20],[6,20],[7,20],[8,20],[9,20],[10,20],[11,20],[[12,20]]]
wafr3 = [[1,20],[2,20],[3,20],[4,20],[5,20],[6,20],[7,20],[8,20],[9,20],[10,20],[11,20],[[12,20]]]
wafr4 = [[1,20],[2,20],[3,20],[4,20],[5,20],[6,20],[7,20],[8,20],[9,20],[10,20],[11,20],[[12,20]]]
wafr5 = [[1,20],[2,20],[3,20],[4,20],[5,20],[6,20],[7,20],[8,20],[9,20],[10,20],[11,20],[[12,20]]]

a = [[]]

def availsize(x):
    k = 0
    for a in x:
        k = k + a[1]
    return k

def eoh(x):
    eoh = 0
    for k in x:
        for j in range(0,len(k)-1):
            eoh = eoh + k[j][1]
        eoh = eoh + availsize(k[-1])
    return eoh

def amount(x):
    mount = []
    for k in range(0,5):
        if x[k] < 15:
            mount.append([k,0])
        else:
            mount.append([k,x[k]])
    count = 0
    for k in mount:
        if k[1] == 0:
            count = count + 1
    totaling = 130*(1-0.02*count)
    if availsize(mount) <= totaling:
        product = [mount[0][1],mount[1][1],mount[2][1],mount[3][1],mount[4][1]]
    else:
        b = sorted(mount, key=lambda x:x[1], reverse=False)
        for k in range(0,5):
            if b[k][1] >0:
                if availsize(b) > totaling:
                    b[k][1] = 25
        remain = totaling - availsize(b)
        index = []
        for k in range(0,5):
            if b[k][1] == 25:
                index.append(k)
        i = max(index)
        b[i][1] = 25 + remain
        end = sorted(b,key=lambda x:x[0], reverse=False)
        product = [end[0][1],end[1][1],end[2][1],end[3][1],end[4][1]]
    return product

def consume(x,y):
    consumelist = []
    if availsize(x) <= y:
        for k in x:
            consumelist.append(k)
            x.clear()
        return [x,consumelist]
    else:
        total = 0
        while total + x[0][1] < y:
            consumelist.append(x[0])
            total = total + x[0][1]
            x.remove(x[0])
        remain = y - total
        x[0][1] = x[0][1] - remain
        consumelist.append([x[0][0],remain])
        return [x,consumelist]

def pkg_process(line,input,output,check,regression):
    last1 = line[0][-1].copy()
    last2 = line[1][-1].copy()
    last3 = line[2][-1].copy()
    last4 = line[3][-1].copy()
    last5 = line[4][-1].copy()
    last1.append([3,line[0][3][1]])
    last2.append([3,line[1][3][1]])
    last3.append([3,line[2][3][1]])
    last4.append([3,line[3][3][1]])
    last5.append([3,line[4][3][1]])
    last = [availsize(last1),availsize(last2),availsize(last3),availsize(last4),availsize(last5)]
    con = amount(last)
    regression.append([sum(con),eoh(line)])
    for i in range(0,5):
        wafer = line[i]
        pkgin = input[i]
        copy = wafer.copy()
        for k in range(1, 4):
            wafer[k] = [copy[k - 1][0] + 1, copy[k - 1][1]]
        wafer[0] = [1, pkgin]
        for a in copy[4]:
            a[0] = a[0] + 1
        copy[4].append([5, copy[3][1]])
        [z, out] = consume(copy[4], con[i])
        for k in out:
            output.append(k)
    check.append(sum(con))
    return [line,output,con]

def fab_process(line,input,output,regression):
    last1 = line[0][-1].copy()
    last2 = line[1][-1].copy()
    last3 = line[2][-1].copy()
    last4 = line[3][-1].copy()
    last5 = line[4][-1].copy()
    last1.append([11, line[0][10][1]])
    last2.append([11, line[1][10][1]])
    last3.append([11, line[2][10][1]])
    last4.append([11, line[3][10][1]])
    last5.append([11, line[4][10][1]])
    last = [availsize(last1), availsize(last2), availsize(last3), availsize(last4), availsize(last5)]
    con = amount(last)
    regression.append([sum(con),eoh(line)])
    for i in range(0,5):
        wafer = line[i]
        fabin = input[i]
        copy = wafer.copy()
        for k in range(1,11):
            wafer[k] = [copy[k-1][0]+1,copy[k-1][1]]
        wafer[0] = [1,fabin]
        for a in copy[11]:
            a[0] = a[0] + 1
        copy[11].append([11,copy[10][1]])
        [z,out] = consume(copy[11],con[i])
        for k in out:
            output.append(k)
    return [line,output,con]

def step(fab,pkg,input,output,output1,t,rato,regression,regression1,check,fill):
    fab_line1 = fab[0]
    fab_line2 = fab[1]
    fab_line3 = fab[2]
    fab_line4 = fab[3]
    pkg_line1 = pkg[0]
    pkg_line2 = pkg[1]
    pkg_line3 = pkg[2]
    pkg_line4 = pkg[3]
    [fab_result1,output,con1] = fab_process(fab_line1,input[0],output,regression)
    [fab_result2,output,con2] = fab_process(fab_line2,input[1],output,regression)
    [fab_result3,output,con3] = fab_process(fab_line3,input[2],output,regression)
    [fab_result4,output,con4] = fab_process(fab_line4,input[3],output,regression)
    pkg_in = [con2[0]+con3[0],con3[1]+con4[0],con1[0]+con3[2],con2[1]+con4[1],con2[2]+con4[2],con3[3]+con4[3],con1[1]+con2[3],con1[2]+con2[4],con1[3]+con4[4],con1[4]+con3[4]]
    [pkg_result1,output1,conn1] = pkg_process(pkg_line1,[rato[1,0,t]*pkg_in[1],rato[3,0,t]*pkg_in[3],rato[4,0,t]*pkg_in[4],rato[5,0,t]*pkg_in[5],rato[6,0,t]*pkg_in[6]],output1,check,regression1)
    [pkg_result2,output1,conn2] = pkg_process(pkg_line2,[rato[0,1,t]*pkg_in[0],rato[2,1,t]*pkg_in[2],rato[5,1,t]*pkg_in[5],rato[8,1,t]*pkg_in[8],rato[9,1,t]*pkg_in[9]],output1,check,regression1)
    [pkg_result3,output1,conn3] = pkg_process(pkg_line3,[rato[2,2,t]*pkg_in[2],rato[3,2,t]*pkg_in[3],rato[4,2,t]*pkg_in[4],rato[7,2,t]*pkg_in[7],rato[9,2,t]*pkg_in[9]],output1,check,regression1)
    [pkg_result4,output1,conn4] = pkg_process(pkg_line4,[rato[0,3,t]*pkg_in[0],rato[1,3,t]*pkg_in[1],rato[6,3,t]*pkg_in[6],rato[7,3,t]*pkg_in[7],rato[8,3,t]*pkg_in[8]],output1,check,regression1)
    fill.append([conn2[0]+conn4[0],conn1[0]+conn4[1],conn2[1]+conn3[0],conn1[1]+conn3[1],conn1[2]+conn3[2],conn1[3]+conn2[2],conn1[4]+conn4[2],conn3[3]+conn4[3],conn2[3]+conn4[4],conn2[4]+conn3[4]])
    return

FAB_origin = [[[[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9], [25, 10],
                            [25, 11], [[25, 12]]],
                           [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9], [25, 10],
                            [25, 11], [[25, 12]]],
                           [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9], [25, 10],
                            [25, 11], [[25, 12]]],
                           [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9], [25, 10],
                            [25, 11], [[25, 12]]],
                           [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9], [25, 10],
                            [25, 11], [[25, 12]]]], [
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]]], [
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]]], [
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]],
                              [[25, 1], [25, 2], [25, 3], [25, 4], [25, 5], [25, 6], [25, 7], [26, 8], [25, 9],
                               [25, 10], [25, 11], [[25, 12]]]]]

PKG_origin = [
                [[[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]], [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]],
                 [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]], [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]],
                 [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]]],
                [[[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]], [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]],
                 [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]], [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]],
                 [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]]],
                [[[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]], [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]],
                 [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]], [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]],
                 [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]]],
                [[[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]], [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]],
                 [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]], [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]],
                 [[25, 1], [25, 2], [25, 3], [25, 4], [[25, 5]]]]]

