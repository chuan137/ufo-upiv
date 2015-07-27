from gi.repository import Ufo

class TaskGraph(Ufo.TaskGraph):
    def connect_branch(self, node_list):
        for i in range(len(node_list)-1):
            n0 = node_list[i]
            n1 = node_list[i+1]
            self.connect_nodes(n0, n1)
    def merge_branch(self, nlist1, nlist2, nodes):
        if isinstance(nlist1, list):
            n1 = nlist1[-1]
        else:
            n1 = nlist1
        if isinstance(nlist2, list):
            n2 = nlist2[-1]
        else:
            n2 = nlist2
        if isinstance(nodes, list):
            self.connect_nodes_full(n1, nodes[0], 0)
            self.connect_nodes_full(n2, nodes[0], 1)
            self.connect_branch(nodes)
        else:
            self.connect_nodes_full(n1, nodes, 0)
            self.connect_nodes_full(n2, nodes, 1)


