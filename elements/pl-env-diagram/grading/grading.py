try:
    import autoeval
except:
    import grading.autoeval as autoeval
import networkx as nx

def process_dict(d, keys_to_keep=[], entries_to_add = {}):
    d = {key: d[key] for key in keys_to_keep if key in d}
    d.update(entries_to_add)
    return d

def convert_parent_index_to_pl_key(parent_index):
    parent_index = parent_index.lower().strip()
    if parent_index[0] == "g":
        return "frame-0"
    else: 
        return "frame-" + parent_index[1:]
    
def add_value_node(G, node_name, value_obj, type_name):
    """Takes in a dictionary with 'val' as a key, 
    and possibly also 'name' as a key. Adds to graph G
    a node representing the value/binding, and """
    
    if value_obj['val'] and value_obj['val'][0] == "#":
        G.add_node(node_name, **process_dict(value_obj, ['name'], {'type': type_name}))
        G.add_edge(node_name, value_obj['val'][1:]) # point to heap object
    else: 
        G.add_node(node_name, **process_dict(value_obj, ['name', 'val'], {'type': type_name}))

def make_graph(env_diagram_obj):
    G = nx.DiGraph()
    for frame in env_diagram_obj['frame']:
        this_frame_key = "frame-" + frame['frameIndex']
        G.add_node(this_frame_key, **process_dict(frame, ["name"], {'type': 'frame'}))
        if "parent" in frame:
            G.add_edge(convert_parent_index_to_pl_key(frame['parent']), this_frame_key)
        for binding in frame['var']:
            binding_key = this_frame_key + "-var-" + str(binding['varIndex'])
            add_value_node(G, binding_key, binding, "binding")
    if 'heap' in env_diagram_obj: 
        for sequence_type_name in ("list", "tuple"):
            if sequence_type_name in env_diagram_obj["heap"]:
                for sequence in env_diagram_obj["heap"][sequence_type_name]:
                    sequence_key = "heap-" + sequence_type_name + "-" + str(sequence[sequence_type_name + "Index"])
                    G.add_node(sequence_key, type=sequence_type_name)
                    prev_node_name = sequence_key
                    for item in sequence["item"]:
                        item_key = sequence_key + "-item-" + str(item['itemIndex'])
                        add_value_node(G, item_key, item, "item")
                        G.add_edge(prev_node_name, item_key)
                        prev_node_name = item_key
        if 'func' in env_diagram_obj['heap']:
            for function in env_diagram_obj['heap']['func']:
                function_key = 'heap-func-' + str(function['funcIndex'])
                G.add_node(function_key, **process_dict(function, ['name'], {'type': 'func'}))
                G.add_edge(function_key, convert_parent_index_to_pl_key(function['parent']))
    return G

def node_subst_cost(node1, node2):
    """Returns a number between 0 and 1"""
    if node1['type'] != node2['type']:
        return 1
    type_name = node1['type']
    if type_name == "binding":
        if 'val' in node1 and 'val' in node2: 
            return (node1['name'] != node2['name']) + (node1['val'] != node2['val'])
        else: 
            return int(node1['name'] != node2['name'])
        # Note that in the case where there is one node that has a pointer and one node
        # that does not have a pointer, the error will be handled by the edge function.
    else:
        return int(node1 != node2)
    
def node_del_cost(node):
    type_name = node['type']
    if type_name == "binding":
        return 2
    else: 
        return 1
    
def node_ins_cost(node):
    type_name = node['type']
    if type_name == "binding":
        return 2
    else: 
        return 1

def grading(generated_json, student_json, partial_credit = "partial"):
    """ returns score and feedback (if applicable) for the student.
    
    options for partial_credit include:
    "none" --> no partial credit
    "partial" --> gets credit per correct frame, and lose points for extra frames. if heap is not identical, loses 1/3 credit."""
    correct_graph = make_graph(generated_json)
    submitted_graph = make_graph(student_json)
    if partial_credit == "partial":
        upper_bound = 10
        dist = nx.graph_edit_distance(
            submitted_graph, 
            correct_graph,
            node_subst_cost=node_subst_cost,
            node_del_cost=node_del_cost,
            node_ins_cost=node_ins_cost,
            upper_bound=upper_bound
        )
        if dist is None: 
            return 0, ""
        return (upper_bound - dist)/upper_bound, ""
    elif partial_credit == "none":
        is_isomorphic = nx.is_isomorphic(submitted_graph, correct_graph, node_match=lambda x, y: x == y)
        return int(is_isomorphic), ""
  
def check_validity(student_input):
    return 1, None

def get_correctAnswerJSON(codestring):
    return autoeval.FrameTree(codestring).generate_html_json()

# import json
# corr = """{"heap":{"func":[{"name":"h","parent":"Global","funcIndex":0,"nameWidth":2}],"list":[{"item":[{"val":"-7","valWidth":3,"itemIndex":0},{"val":"'dan garcia'","valWidth":13,"itemIndex":1},{"val":"9","valWidth":2,"itemIndex":2,"isLastElement":true}],"listIndex":0}],"tuple":[]},"frame":[{"var":[{"val":"-7","name":"b","valWidth":3,"varIndex":0,"nameWidth":2},{"val":"'dan garcia'","name":"w","valWidth":13,"varIndex":1,"nameWidth":2},{"val":"#heap-func-0","name":"h","varIndex":2,"nameWidth":2},{"val":"#heap-list-0","name":"c","varIndex":3,"nameWidth":2}],"frameIndex":"0"},{"var":[{"val":"9","name":"c","valWidth":2,"varIndex":0,"nameWidth":2}],"name":"h","parent":"Global","return":{"val":"#heap-list-0"},"nameWidth":2,"frameIndex":"1"}]}"""
# test = """{"heap":{"func":[{"name":"h","parent":"Global","funcIndex":0,"nameWidth":2}],"list":[{"item":[{"val":"7","valWidth":3,"itemIndex":0},{"val":"'dan garcia'","valWidth":13,"itemIndex":1},{"val":"9","valWidth":2,"itemIndex":2,"isLastElement":true}],"listIndex":0}],"tuple":[]},"frame":[{"var":[{"val":"-7","name":"b","valWidth":3,"varIndex":0,"nameWidth":2},{"val":"'dan garcia'","name":"w","valWidth":13,"varIndex":1,"nameWidth":2},{"val":"#heap-func-0","name":"h","varIndex":2,"nameWidth":2},{"val":"#heap-list-0","name":"c","varIndex":3,"nameWidth":2}],"frameIndex":"0"},{"var":[{"val":"9","name":"c","valWidth":2,"varIndex":0,"nameWidth":2}],"name":"h","parent":"Global","return":{"val":"#heap-list-0"},"nameWidth":2,"frameIndex":"1"}]}"""
# corr = json.loads(corr)
# test = json.loads(test)
# print(grading(corr, test))