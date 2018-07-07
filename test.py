#coding:utf-8#

#Besoin de ça pour le hashmap
'''dico = dict()

dico['prout'] = [[(12,22),(34,56)],"zerg"]

print(dico)

new = (23,43)
old = (12,22)
print(dico['prout'][0])
if new not in dico['prout'][0]:
    print("on add")

if old not in dico['prout'][0]:
    print("on add")

if 'prout' in dico:
    print("prout")

if 'caca' in dico:
    print("caca")


key = "caca"
print(dico.get(key))
dico_prout = dico.get(key)
if dico_prout != None:
    dico_prout[0].append((67,89))
else:
    dico_prout = [[],"protoss"]

print(dico)
'''
# si le dico existe pas deja
    # on init le dico
# sinon
    # on update juste les coor des units

import time
start_time = time.time()


indexes = list(range(1, 2000))

w = 200

#x = 199
#y = 1

for index in indexes:
    y = index / w
    x = index - (w * int(y))


# 0.0009

'''
    y = index/w
    x = (y - int(y)) * w
'''


#print(int(y))
#print(int(x))
print("--- %s seconds ---" % (time.time() - start_time))
