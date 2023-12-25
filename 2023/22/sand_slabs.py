import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", help="use test input",
                    action="store_true")
args = parser.parse_args()

filename = '22/input'
if args.test:
    filename='22/test.txt'


def get_direction(vector):
    dr = ""
    if vector.real > 0:
        dr += 'D'
    if vector.real < 0:
        dr += 'U'
    if vector.imag > 0:
        dr += 'R'
    if vector.imag < 0:
        dr += 'L'
    return dr

def to_complex(x: int,y: int) -> complex:
    return x*1j+y


class Block():
    comp: list[complex]
    name: str
    zs: tuple[int]
    def __init__(self,coor1,coor2, name=''):
        self.comp = tuple([to_complex(c[0],c[1]) for c in [coor1,coor2]])
        self.zs = tuple(range(coor1[2],coor2[2]+1))
        self.name = name
        if self.name == '':
            self.name = str([coor1,coor2])

    @classmethod
    def from_string(cls,line, name=None):
        name_ls = []
        if name is not None:
            name_ls = [name]
        return cls(*[[int(c) for c in t.strip().split(',')] for t in line.split('~')]+name_ls)
    
    @property
    def minz(self):
        return min(self.zs)
    
    @property
    def maxz(self):
        return max(self.zs)
    
    def move_down(self, amount=1):
        self.zs = tuple([z-amount for z in self.zs])
   
    @staticmethod
    
    
    def coordinates(self):
        xs = [self.comp[0].imag,self.comp[1].imag]
        ys = [self.comp[0].real,self.comp[1].imag]
        zs = self.zs
        return list(zip(xs,ys,zs))
    
    # returns True if two blocks could collide if on the same z position
    def could_collide(self,other: 'Block'):
        a = self.comp[0]
        b = self.comp[1]
        c = other.comp[0]
        d = other.comp[1]
        #cd is a point
        if c==d:
            return ( (c.real <= max(a.real, b.real)) and (c.real >= min(a.real, b.real)) and 
                (c.imag <= max(a.imag, b.imag)) and (c.imag >= min(a.imag, b.imag)))
        #ab is a point
        if a==b:
            return ( (a.real <= max(c.real, d.real)) and (a.real >= min(c.real, d.real)) and 
                (a.imag <= max(c.imag, d.imag)) and (a.imag >= min(c.imag, d.imag)))
        if get_direction(b-a) == get_direction(d-c) or get_direction(b-a) == get_direction(c-d):
            #Lines are colinear
            if ( (c.real <= max(a.real, b.real)) and (c.real >= min(a.real, b.real)) and 
                (c.imag <= max(a.imag, b.imag)) and (c.imag >= min(a.imag, b.imag))): 
                return True
            if ( (d.real <= max(a.real, b.real)) and (d.real >= min(a.real, b.real)) and 
                (d.imag <= max(a.imag, b.imag)) and (d.imag >= min(a.imag, b.imag))):
                return True
            if ( (a.real <= max(c.real, d.real)) and (a.real >= min(c.real, d.real)) and 
                (a.imag <= max(c.imag, d.imag)) and (a.imag >= min(c.imag, d.imag))):
                return True
            if ( (b.real <= max(c.real, d.real)) and (b.real >= min(c.real, d.real)) and 
                (b.imag <= max(c.imag, d.imag)) and (b.imag >= min(c.imag, d.imag))):
                return True
            return False
        if get_direction(d-a) == get_direction(c-a):
            return False
        if get_direction(d-b) == get_direction(c-b):
            return False
        if get_direction(a-c) == get_direction(b-c):
            return False
        if get_direction(a-d) == get_direction(b-d):
            return False
        return True
        
    
    def __repr__(self):
        return f"'name': {self.name}, 'comp': {self.comp}, 'zs': {self.zs}"





class Blocks():
    blocks: set[Block]
    _sorted_blocks: list[Block]
    def __init__(self,*blocks):
        self.blocks = set(blocks)
        self._sorted_blocks = None
        self.num_of_blocks = len(self.blocks)
        self.u_adj_list = {block: set() for block in self.blocks}
        self.d_adj_list = {block: set() for block in self.blocks}
        self.z_dict = {k:[] for k in range(1,self.maxz+1)}
        self.max_processed_z = 0


        for block in blocks:
            for z in block.zs:
                self.z_dict[z].append(block)


    @classmethod
    def from_file(cls,filename: str):
        with open(filename, 'r') as stream:
            lines = [l.strip() for l in stream.readlines()]
        blocks = [Block.from_string(b,i) for i,b in enumerate(lines)]
        return cls(*blocks)
    
    @property
    def sorted_blocks(self):
        if self._sorted_blocks is None:
            self._sorted_blocks = sorted(self.blocks,key=lambda b: min(b.zs))
        return self._sorted_blocks
    
    def get_block_index(self,block):
        return self.sorted_blocks.index(block)

    def get_block(self, name):
        return [b for b in self.blocks if b.name == name][0]
    
    def add_on_top(self,b1,b2):
        self.u_adj_list[b1].add(b2)

    def add_underneath(self,b1,b2):
        self.d_adj_list[b1].add(b2)
    
    def move_down(self,block: Block):
        orig_zs = block.zs
        # If this element is at the bottom, move to z pos 1
        if block.minz == self.minz:
            block.move_down(block.minz-1)
            self.update_z_dict(block,orig_zs)
            return
        z = 0
        for z in range(-1,-block.minz,-1):
            if self.z_dict[block.minz+z] != []:
                break
        if z < 0:
            block.move_down(abs(z)-1)
        while self._try_move_down(block):
            continue
        if block.minz < block.minz+z:
            self._sorted_blocks = None
        self.update_z_dict(block,orig_zs)

    def find_edges(self):
        for block in self.blocks:
            self.find_edge(block)

    def find_edge(self,block):
        if block.minz > 1:
            for other in self.z_dict[block.minz-1]:
                if block.could_collide(other):
                    self.add_on_top(other,block)
                    self.add_underneath(block,other)

    def update_z_dict(self, block:Block, orig_z:tuple[int]):
        add_zs = [z for z in block.zs if z not in orig_z]
        rem_zs = [z for z in orig_z if z not in block.zs]
        for z in rem_zs:
            self.z_dict[z].remove(block)
        for z in add_zs:
            self.z_dict[z].append(block)

    def can_move_down(self, block:Block):
        new_minz = block.minz -1
        if new_minz < 1:
            return False
        for b in self.z_dict[new_minz]:
            if block.could_collide(b):
                return False
        return True
    
    @property
    def maxz(self):
        return max([block.maxz for block in self.blocks])
    
    @property
    def minz(self):
        return min([block.minz for block in self.blocks])

    def _try_move_down(self,block):
        if self.can_move_down(block):
            block.move_down()
            return True
        return False
    
    def move_all(self):
        for block in self.sorted_blocks:
            self.move_down(block)
    
    def process(self):
        self.move_all()
        self.find_edges()
    
    @property
    def necessary(self):
        return set().union(*[self.d_adj_list[n] for n,e in self.d_adj_list.items() if len(e) == 1])
    
    @property
    def removeable(self):
        return set([b for b in self.blocks if b not in self.necessary])
    
    def count_supports(self, block):
        chain = set()
        q = [block]
        while len(q) > 0:
            q.sort(key=lambda b: b.minz)
            block = q.pop(0)
            if block in chain:
                continue
            chain.add(block)
            for b in self.u_adj_list[block]:
                in_chain = True
                for s in self.d_adj_list[b]:
                    if s not in chain:
                        in_chain = False
                if in_chain:
                    q.append(b)
        return len(chain)-1


def main():
    print('parsing...')
    blocks = Blocks.from_file(filename)

    print('moving...')
    blocks.move_all()

    print('finding edges...')
    blocks.find_edges()

    print('finding removeable...')
    answer1 = len(blocks.removeable)

    print('counting..')
    answer2 = sum([blocks.count_supports(b) for b in blocks.necessary])

    print('done')

    print(f"Answer 1: {answer1}")
    print(f"Answer 2: {answer2}")

if __name__ == '__main__':
    main()