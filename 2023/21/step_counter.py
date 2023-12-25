import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", help="increase output verbosity",
                    action="store_true")
args = parser.parse_args()

filename = 'input'
if args.test:
    filename='test.txt'

with open(filename, 'r') as stream:
    lines = [l.rstrip() for l in stream.readlines()]

gardens = []
rocks = []
start = 0
grid = []

for i,l in enumerate(lines):
    for j,x in enumerate(l):
        v = i+(j*1j)
        grid.append(v)
        if x == '#':
            rocks.append(v)
        if x == '.':
            
            gardens.append(v)
        if x == 'S':
            gardens.append(v)
            start = v

def pp_off(x,y,mar):
    count = 0
    xoff = x*131
    yoff = y*131
    pp = [['.' for x in range(131)] for y in range(131)]
    for spot in mar:
        i = int(spot.real)
        j = int(spot.imag)
        yi = i- yoff
        xj = j- xoff
        if 0 <= yi < 131 and 0 <= xj < 131:
            pp[yi][xj] = 'O'
            count += 1
    for a in rocks:
        i = int(a.real)
        j = int(a.imag)
        pp[i][j] = '#'
    print("\n".join(["".join([x for x in l]) for l in pp]))
    return count

def count_off(x,y,mar):
    count = 0
    xoff = x*131
    yoff = y*131
    for spot in mar:
        i = int(spot.real)
        j = int(spot.imag)
        yi = i- yoff
        xj = j- xoff
        if 0 <= yi < 131 and 0 <= xj < 131:
            count += 1
    return count


def rec(pos,depth,marked,count=0) -> set[complex]:
    np = (int(pos.real)%131)+(int(pos.imag)%131)*1j
    if np not in gardens:
    # if pos not in gardens:
        return set()
    if count == depth:
        if pos in marked:
            return set()
        marked.add(pos)
        return {pos}
    ret = set()
    for d in [1,-1,1j,-1j]:
        if d+pos not in marked:
            ret = ret.union(rec(d+pos,depth,marked,count+1))
    return ret

def run(desire):
    off = 1
    if desire%2 == 0:
        off = 2
    cc = set()
    mk = set()
    aa = rec(start,off, cc)
    mk = mk.union(aa)
    for i in range(int((desire-off)/2)):
        bs = set()
        for a in aa:
            bb = rec(a,2,cc)
            bs = bs.union(bb)
        mk = mk.union(cc)
        cc = aa.union(bs)
        aa = bs
    return mk

#part 1
answer = len(run(64))

print(f"Answer 1: {answer}")

#part 2

desire = 65+131+131
a2 = run(desire)

odd_s_corner = count_off(0,2,a2)
odd_n_corner = count_off(0,-2,a2)
odd_e_corner = count_off(-2,0,a2)
odd_w_corner = count_off(2,0,a2)
g1 = count_off(0,0,a2) #odd grid
g2 = count_off(1,0,a2) #Even grid
even_small_ne = count_off(-1,-2,a2)
even_small_nw = count_off(1,-2,a2)
even_small_se = count_off(-1,2,a2)
even_small_sw = count_off(1,2,a2)
odd_large_ne = count_off(-1,-1,a2)
odd_large_nw = count_off(1,-1,a2)
odd_large_se = count_off(-1,1,a2)
odd_large_sw = count_off(1,1,a2)


cb1 = odd_n_corner + odd_e_corner + odd_s_corner + odd_w_corner #odd corners
cb2 = even_small_ne + even_small_nw + even_small_se + even_small_sw # even small sides
cb3 = odd_large_ne + odd_large_nw + odd_large_se + odd_large_sw # odd large side

ca2 = 4*g1-cb3
ca3 = 4*g2-cb2
ca1 = ca3-cb2

# ca1 = count_off(0,1,a1)+count_off(0,-1,a1)+count_off(1,0,a1)+count_off(-1,0,a1) # even corner
# ca2 = count_off(1,1,a1)+count_off(-1,1,a1)+count_off(1,-1,a1)+count_off(-1,-1,a1) # odd small side
# ca3 = count_off(1,2,a3)+count_off(-1,2,a3)+count_off(-2,-1,a3)+count_off(2,-1,a3) # even large side

foone = lambda n: ((n+(n%2)-1)**2)*g1+(4*(n//2)**2)*g2+cb1+n*cb2+(n-1)*cb3 #For even depth
foono = lambda n: ((n+(n%2)-1)**2)*g1+(4*(n//2)**2)*g2+ca1+n*ca2+(n-1)*ca3 #For odd depth
foo = lambda n: foone(n) if n%2==0 else foono(n)

n = (26501365-65)/131

answer = foo(n)
print(f"Answer 2: {answer}")