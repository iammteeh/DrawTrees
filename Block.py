class Block:
    def __init__(self, nodes: list[str], levels: list[int], predecessors: list[str], successors: list[str], id=-1):
        self.id = id
        self.nodes = nodes
        self._upper = nodes[0]
        self._lower = nodes[-1]
        self.levels = levels
        self._predecessors = predecessors
        self._successors = successors
        self.i_p = []
        self.i_n = []
        pass

    @property
    def upper(self) -> str:
        return self._upper

    @property
    def lower(self) -> str:
        return self._lower

    @property
    def n_n(self) -> list[str]:
        return self._predecessors

    @n_n.setter
    def n_n(self, value: list[str]) -> None:
        self._predecessors = value

    @property
    def n_p(self) -> list[str]:
        return self._successors

    @n_p.setter
    def n_p(self, value: list[str]) -> None:
        self._successors = value

    def clear(self):
        self.i_n.clear()
        self.i_p.clear()
        self._predecessors.clear()
        self._successors.clear()

    def __str__(self):
        return f"id: {self.id}, nodes{self.nodes}"


class BlockList:
    def __init__(self):
        self.blocks: dict[int, Block] = {}
        self.block_order: list[int] = []

    def add_block(self, B: Block) -> int:
        block = len(self.block_order)
        B.id = block
        self.blocks[block] = B
        self.block_order.append(block)
        return block

    def new_block_number(self) -> int:
        return len(self.block_order)

    def pi(self, block: int):
        return self.block_order.index(block)

    def move(self, block: Block, pi):
        old_pos = self.block_order.index(block.id)
        self.block_order.remove(block.id)

        if pi > old_pos:
            pi = pi - 1

        self.block_order.insert(pi, block.id)

    def swap_pos(self, id_A: int, id_b: int):
        pos_a = self.block_order.index(id_A)
        pos_b = self.block_order.index(id_b)

        self.block_order[pos_a] = id_b
        self.block_order[pos_b] = id_A

    def __len__(self):
        return len(self.block_order)

    def block_from_id(self, id: int) -> Block:
        return self.blocks[id]

    def block_from_pos(self, pos: int) -> Block:
        return self.blocks[self.block_order[pos]]

    def __getitem__(self, pos):
        return self.block_from_pos(pos)

    def __str__(self):
        # return str(self.blocks)
        return ''