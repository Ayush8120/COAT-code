'''
collection of tuples for generating F_ideal and F_moderate datasets
'''
idealDataset = {
    2: [(0,0,1),(0,1,0),(1,0,0)],
    3: [(0,0,2),(0,1,1),(1,0,1),(0,2,0),(1,1,0),(2,0,0),],
    4: [(1,1,1),(3,0,0),(0,3,0),(0,0,3),(1,2,0),(1,0,2),(2,1,0),(2,0,1),(0,1,2),(0,2,1)],
    5: [(1,1,2),(2,1,1),(1,2,1),(0,1,3),(0,3,1),(1,0,3),(1,3,0),(3,0,1),(3,1,0),(4,0,0),(0,4,0),(0,0,4)]
}
#(context,concept,random) - going radially out of the hierarchy
#make 3 pouches : context (mod,bad) + concept (ideal,mod,bad) i.e not in context +  random (ideal,mod,bad)
