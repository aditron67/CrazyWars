a = ()
print(a)
a = (1, 2, 3)
print(a)
a = (1, "hello", 3.14159265)
print(a)
a = ("Aopple", [1, 2, 3], ("un", "2", 3.00, "cuatro"))
print(a)
a = (1,2,3,4,2,4,4,5,56,547,6,7,43,346,54,5,523,44,2 )
print(a[1])
print(a[0])
m_tuple = ("bannana frog", [2,4,6,8], ("un", 2, "cat", 4.0))
print(m_tuple[0][2])
print(m_tuple[1][2])
print("sliced: ", m_tuple[2][1])
for letter in a:
    print("hello",letter)
ms = {1,2,121,2,3,4,2,1,3,1,34,1,3,4,5,6,7,8,9,0}
print(ms)
ms.add(2)
print(ms)
set1 = ms
set2 = {1,2,3,4,5,6,7,8,9}
print(set1)
print(set2)
print("difference:")
print(set1.difference(set2))
print("symmetric difference:")
print(set1.symmetric_difference(set2))
mstr1 = {"add", "uno","dos", "tres", "CUATRO"}
mstr2 = {"un", "un", "human", "los", "cat"}
print("original:",  mstr1)
print("original:",  mstr2)
mstr = mstr1.union(mstr2)
print("union:", mstr)
setx = {"bob", "neon", "penguin", "dog"}
sety = {"cat", "dog", "frog", "pengunin"}

setz = setx.intersection(sety)
print("intersection:", setz)
