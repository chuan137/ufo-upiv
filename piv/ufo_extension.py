from gi.repository import Ufo
import types

class TaskGraph(Ufo.TaskGraph):
    def connect_branch(self, node_list):
        if len(node_list) > 1:
            for i in range(len(node_list)-1):
                self.connect_nodes(node_list[i], node_list[i+1])

    def merge_branch(self, nlist1, nlist2, nlist3):
        # convert everything to list
        if type(nlist1) is not list:
            nlist1 = [nlist1]
        if type(nlist2) is not list:
            nlist2 = [nlist2]
        if type(nlist3) is not list:
            nlist3 = [nlist3]

        self.connect_branch(nlist1)
        self.connect_branch(nlist2)
        self.connect_branch(nlist3)
        self.connect_nodes_full(nlist1[-1], nlist3[0], 0)
        self.connect_nodes_full(nlist2[-1], nlist3[0], 1)

class PluginManager(Ufo.PluginManager):
    def get_task(self, task, **kwargs):
        t = super(PluginManager, self).get_task(task)
        t.set_properties(**kwargs)
        return t
