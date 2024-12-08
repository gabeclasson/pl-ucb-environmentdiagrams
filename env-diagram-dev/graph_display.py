import networkx as nx
import matplotlib.pyplot as plt

correct = {'directed': False, 'multigraph': False, 'graph': {}, 'nodes': [{'type': 'frame', 'id': 'frame-0'}, {'name': 'x', 'val': '"hello"', 'type': 'binding', 'id': 'frame-0-var-0'}, {'name': 'y', 'type': 'binding', 'id': 'frame-0-var-1'}, {'type': 'sequence', 'sequence_type': 'list', 'id': 'heap-list-0'}, {'val': '5', 'type': 'item', 'id': 'heap-list-0-item-0'}, {'val': '4', 'type': 'item', 'id': 'heap-list-0-item-1'}, {'val': '3', 'type': 'item', 'id': 'heap-list-0-item-2'}, {'val': '2', 'type': 'item', 'id': 'heap-list-0-item-3'}, {'val': '1', 'type': 'item', 'id': 'heap-list-0-item-4'}, {'type': 'sequence_end', 'sequence_type': 'list', 'id': 'heap-list-0-end'}], 'links': [{'type': 'binding_pointer', 'source': 'frame-0-var-1', 'target': 'heap-list-0'}, {'type': 'sequence', 'source': 'heap-list-0', 'target': 'heap-list-0-item-0'}, {'type': 'sequence', 'source': 'heap-list-0-item-0', 'target': 'heap-list-0-item-1'}, {'type': 'sequence', 'source': 'heap-list-0-item-1', 'target': 'heap-list-0-item-2'}, {'type': 'sequence', 'source': 'heap-list-0-item-2', 'target': 'heap-list-0-item-3'}, {'type': 'sequence', 'source': 'heap-list-0-item-3', 'target': 'heap-list-0-item-4'}, {'type': 'sequence', 'source': 'heap-list-0-item-4', 'target': 'heap-list-0-end'}]}
incorrect = {'directed': False, 'multigraph': False, 'graph': {}, 'nodes': [{'type': 'frame', 'id': 'frame-0'}, {'name': 'x', 'type': 'binding', 'id': 'frame-0-var-0'}, {'id': 'heap-list-0'}], 'links': [{'type': 'binding_pointer', 'source': 'frame-0-var-0', 'target': 'heap-list-0'}]}

H = nx.node_link_graph(correct)

nx.draw(H)
nodes = nx.draw(H, pos=nx.spring_layout(H), with_labels = True)

plt.show()