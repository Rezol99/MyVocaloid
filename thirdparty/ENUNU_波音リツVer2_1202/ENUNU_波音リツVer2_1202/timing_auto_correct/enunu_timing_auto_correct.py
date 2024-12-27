#Copyright (c) 2022 Canon
import sys
import os
#from tkinter import messagebox

# メッセージボックス（情報） 
# messagebox.showinfo('確認', 'あああ')

args = sys.argv
current = os.path.dirname(args[0])
#args = ['path','--mono_score','C:\\Users\canon\\Desktop\\python_code\\Gekko_Rhapsody_1ban__20220120121548_mono_score.lab','--mono_align','C:\\Users\\canon\\Desktop\\python_code\\Gekko_Rhapsody_1ban__20220120121548_timing.lab']
#os.path.dirname(sys.argv(0)) 

set_path = current + "\\settings.txt"
con_path = current + "\\consonant_time.txt"
print (set_path)
print (con_path)
# read settings///////////////////////////////////////
f = open(set_path, 'r', encoding='UTF-8')
con = f.read().split("\n")
f.close()
cnt = 0
for i in con:
    con[cnt] = i.split('=')[1]
    cnt += 1


conson = float(con[0])
if conson > 0.9:
    conson = 0.9
if conson < 0.1:
    conson = 0.1
vow = 1.0 - conson
consonant = 1.0 / conson###0.6 -> 1.666
vowel = 1.0 / vow###0.4 = 2.5

rest_a = float(con[1])
rest_i = float(con[2])
rest_u = float(con[3])
rest_e = float(con[4])
rest_o = float(con[5])
rest_N = float(con[6])
if con[7] == "on" or con[7] == "ON":#add131
    c_list = 1                      #add131
    print ('consonant_list:on')
else:
    c_list = 0
    print ('consonant_list:off')
c_scale = float(con[8])             #add131

#///
if con[9] == '1':
    #print('linkage=1')
    cnt = 1
    for arg1 in args[1:]:
        if arg1 == '--mono_score':
            m_s_p = args[cnt+1]
        if arg1 == '--mono_timing':
            m_a_p = args[cnt+1]
        cnt += 1
else:
   # print(args[0])
   # print(args[1])
    if 'mono_score.lab' in args[1] and 'timing.lab' in args[2]:
        m_s_p = args[1]
        m_a_p = args[2]
    elif 'mono_score.lab' in args[2] and 'timing.lab' in args[1]:
        m_s_p = args[2]
        m_a_p = args[1]
    else:
        print('おかしい')
        input()
        exit()
    
print(m_s_p)
print(m_a_p)
x = '.lab'
if x not in m_s_p:
    print('labない')
if x not in m_a_p:
    print('labない')






# add131 load consonant time//////////////
ct_time = []
f = open(con_path, 'r', encoding='UTF-8')
consonant_time = f.read().split("\n")
cnt_ct = 0
temp_cs= 0.0
for i in consonant_time:
    i = i.split(" ")
    ct_time.append(i)

f.close()
ct_line = len(consonant_time)

for i in ct_time:
    if ct_time[cnt_ct][0] == "":
        break
    
    temp_cs = float(ct_time[cnt_ct][1]) * c_scale
    
    ct_time[cnt_ct][1] = str(temp_cs)
    cnt_ct += 1

#read lab/////////////////////////////////////////////
f = open(m_s_p, 'r', encoding='UTF-8')
mono_rare = f.read().split("\n")
f.close()

f = open(m_a_p, 'r', encoding='UTF-8')
timing_rare = f.read().split("\n")
f.close()

f = open(m_a_p, 'r', encoding='UTF-8')
timing_bak = f.read()
f.close()

cntmono = 0
for i in mono_rare:
    if i == "":
        break
    cntmono +=1
cnttiming = 0
for i in timing_rare:
    if i == "":
        break
    cnttiming +=1
    
if cntmono != cnttiming:
    print('行数違う')
else:
    print('行数同じ')



# 計算と分類
mono = ['']*cntmono
time = ['']*cntmono
mono1n = [0.0]*cntmono
mono2n = [0.0]*cntmono
mono_length = [0.0]*cntmono
time1n = [0.0]*cntmono
time2n = [0.0]*cntmono
time_length = [0.0]*cntmono
types = ['']*cntmono
for i in range(cntmono):
    mono[i] = mono_rare[i].split(' ')
    time[i] = timing_rare[i].split(' ')
    mono1n[i] = float(mono[i][0])
    mono2n[i] = float(mono[i][1])
    mono_length[i] = mono2n[i] - mono1n[i]
    #print(time[i][0])
    time1n[i] = float(time[i][0])
    time2n[i] = float(time[i][1])
    time_length[i] = time2n[i] - time1n[i]
    if mono[i][2] == 'a' or mono[i][2] == 'i' or mono[i][2] == 'u' or mono[i][2] == 'e' or mono[i][2] == 'o' or mono[i][2] == 'N': 
        types[i] = 'v'
    elif mono[i][2] == 'A' or mono[i][2] == 'I' or mono[i][2] == 'U' or mono[i][2] == 'E' or mono[i][2] == 'O': 
        types[i] = 'vl'
    elif mono[i][2] == 'pau' or mono[i][2] == 'sl' or mono[i][2] == 'br':
        types[i] = 'r'
    elif mono[i][2] == 'cl':
        types[i] = 'cl'
    else:
        types[i] = 'c'

#add131 assign fixed number to consonant length

if c_list == 1:
    for i in range(cntmono):
        for j in range(ct_line):
            if mono[i][2] == ct_time[j][0]:
                time_length[i] = float(ct_time[j][1])
                
# 数値入力
last1 = ['']*cntmono
last2 = [0]*cntmono
last3 = ['']*cntmono

for i in range(cntmono):
    last3[i] = mono[i][2]

    if i == 0:
        last1[i] = mono[i][0]
    else:
        last1[i] = last2[i-1]

    if i < cntmono-1:
        if types[i+1] == 'c':#                                         2 if next is consonant
            if types[i] != 'cl':#                                      3 if current is not cl
                if mono_length[i] >= time_length[i+1]*consonant:#      4 if next consonant is long
                    temp_f = mono2n[i] - time_length[i+1]
                    last2[i] = int(temp_f)
                else:# if next consonant is short
                    temp_f = float(last1[i]) + mono_length[i] / vowel
                    last2[i] = int(temp_f)
            else:#                                                     3 if current is cl
                if time_length[i] >=  time_length[i+1]*2: #            4 if next consonant is long
                    temp_f = mono2n[i] - time_length[i+1]
                    last2[i] = int(temp_f)
                else:#                                                 4 if next consonant is short
                    temp_f = float(last1[i]) + time_length[i] / 2
                    last2[i] = int(temp_f) 
        elif types[i+1] == 'cl':#                                       2 if next is cl
            last2[i] = time[i][1]
        else:#                                                         2 if next is not vowel,cl and consonant
            if types[i] == 'r':#                                        3 if current is rest
                if mono[i+1][2] == 'a' and mono_length[i+1] > rest_a + 50000:
                    temp_f = mono1n[i+1] - rest_a
                    last2[i] = int(temp_f)
                elif mono[i+1][2] == 'i' and mono_length[i+1] > rest_i + 50000:
                    temp_f = mono1n[i+1] - rest_i
                    last2[i] = int(temp_f)
                elif mono[i+1][2] == 'u' and mono_length[i+1] > rest_u + 50000:
                    temp_f = mono1n[i+1] - rest_u
                    last2[i] = int(temp_f)
                elif mono[i+1][2] == 'e' and mono_length[i+1] > rest_e + 50000:
                    temp_f = mono1n[i+1] - rest_e
                    last2[i] = int(temp_f)
                elif mono[i+1][2] == 'o' and mono_length[i+1] > rest_o + 50000:
                    temp_f = mono1n[i+1] - rest_o
                    last2[i] = int(temp_f)
                elif mono[i+1][2] == 'N' and mono_length[i+1] > rest_N + 50000:
                    temp_f = mono1n[i+1] - rest_N
                    last2[i] = int(temp_f)
                else: 
                    last2[i] = mono[i+1][0]
            elif types[i+1] == 'vl':#無声子音語尾が消えないように
                if types[i] == 'c':
                    if i < cntmono-2:
                        if types[i+2] == 'r':
                            temp_f = float(mono2n[i+1]) - 50000
                            #temp_f = float(mono2n[i]) + temp_f
                            last2[i] = int(temp_f)
                    
            else:
                last2[i] = mono[i+1][0]
                if last2[i] == "0":       # add131
                    last2[i] = time[i+1][0]# add131
                    
                    

last2[cntmono-1] = mono[cntmono-1][1]
body = ''
for i in range(cntmono):
    #print (last1[i])
    body = body + str(last1[i]) + ' ' + str(last2[i]) + " " + str(last3[i]) + '\n'

#print (body)


map_bak = m_a_p + ".bak"
f = open(map_bak,'w', encoding='UTF-8')
f.write(timing_bak)
f.close()

f = open(m_a_p,'w', encoding='UTF-8')
f.write(body)
f.close()


#input()




















