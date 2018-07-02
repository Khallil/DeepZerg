
dico = dict()

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

# si le dico existe pas deja
    # on init le dico
# sinon
    # on update juste les coor des units