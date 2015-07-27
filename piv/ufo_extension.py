from gi.repository import Ufo

class TaskGraph(Ufo.TaskGraph):
    def connect_branch(self, node_list):
        for i in range(len(node_list)-1):
            n0 = node_list[i]
            n1 = node_list[i+1]
            self.connect_nodes(n0, n1)
    def merge_branch(self, nlist1, nlist2, nlist3):
        try:
            self.connect_branch(nlist1)
            n1 = nlist1[-1]
        except:
            n1 = nlist1
        try:
            self.connect_branch(nlist2)
            n2 = nlist2[-1]
        except:
            n2 = nlist2
        try:
            self.connect_branch(nlist3)
            n3 = nlist3[0]
        except:
            n3 = nlist3
 
        self.connect_nodes_full(n1, n3, 0)
        self.connect_nodes_full(n2, n3, 1)

class PluginManager(Ufo.PluginManager):
    def get_task(self, task, **kwargs):
        t = super(PluginManager, self).get_task(task)
        t.set_properties(**kwargs)
        return t
