from pathlib import Path
import numpy as np

class Vertex():
    #vertex which has unique name and the name of it's adjacent vertex
    def __init__(self,name,adj=""):
        self.name=name
        self.adjacent=adj

class SingleAdjacencyGraph():
    # Graph object that has edges and vertices where every vertex has exactly one adjacent vertex joined by an edge
    def __init__(self,vertices=[]):
        self._vertices=vertices
        self.generate_graph_dict()

    def ascend_graph(self,vertex_name,verbose=False):
        ascension_path=[vertex_name]
        edges=1 #you always travel at least one edge before entering the while loop
        vertex = self._vertex_dict[vertex_name]  #find the vertex object given the key
        adjacent_vertex=vertex.adjacent     #check which vertex this is adjacent to
        if verbose: print("At vertex {}, adjacent to {}".format(vertex.name,vertex.adjacent,edges))
        while adjacent_vertex!="COM":
            ascension_path.append(adjacent_vertex) #add the next vertex to the path you take
            if adjacent_vertex=="":  #if there is no adjacent vertex throw an error
                raise ValueError("Vertex has no adjacency")
            vertex=self._vertex_dict[adjacent_vertex]  #move to the adjacent vertex
            adjacent_vertex=vertex.adjacent
            edges+=1    #add 1 to the number of edges travelled
            if verbose: print("At vertex {}, adjacent to {}".format(vertex.name, vertex.adjacent, edges))
        ascension_path.append("COM")
        return edges,ascension_path

    def generate_graph_dict(self):
        self._vertex_dict={vertex.name:vertex for vertex in self._vertices}


    def add_vertex(self,vertex):
        self._vertices.append(vertex)

    @property
    def vertices(self):
        return self._vertices

def vertex_from_input(input_string):
    adjacent,name=input_string.strip().split(")")
    return Vertex(name,adjacent)

def puzzle_part_a(graph):
    # count the total direct and indirect orbits in tree
    indirect_orbits = [graph.ascend_graph(vertex.name)[0] for vertex in graph.vertices]
    print("Total of {} direct and indirect orbits in graph".format(np.sum(indirect_orbits)))

def puzzle_part_b(graph):
    # figure out how far apart you are from santa
    # find the vertices traversed for you as a list and the vertices traversed from santa
    _,path_you=graph.ascend_graph("YOU")
    _,path_san=graph.ascend_graph("SAN")
    path_you.reverse()
    path_san.reverse()
    #print(path_you)
    #print(path_san)
    steps_to_santa=len(set(path_you)^set(path_san))-2 #have to subtract 2 because your trying to move from your adjacent vertex to santas
    print("you are {} orbits away from santa".format(steps_to_santa))

def main():
    puzzle_input_path=Path("puzzle_inputs") / "day6_input.txt"
    vertices=[] #list that hold the vertices to be passed to graph
    with open(puzzle_input_path) as file:
       vertices=[vertex_from_input(line) for line in file.readlines()]
    graph=SingleAdjacencyGraph(vertices)
    puzzle_part_a(graph)
    puzzle_part_b(graph)



if __name__=="__main__":
    main()