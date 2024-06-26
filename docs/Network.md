# `Network` class

This class is responsible for modeling the network between nodes, which in this tool are the balloons. We use a store-and-forward type of network, that uses other networks to "hop" from a source to a destination.

We use the `Networkx` plugin to create a weighted (using receiver power; see [NetworkAnalyzer](./NetworkAnalyzer.md)) graph of all of the nodes. We additionally use the plugin to calculate a "contact graph", which denotes the path messages should take when hopping from node-to-node to get from a source node to a destination node. Currently, the best path between any two nodes is chosen to be the path with the overall highest receiver power, as well as including the most nodes. We call this the "most inclusive" path.

This network is a stripped-away version of Delay (or Disruption) Tolerant Networks (DTNs). If you're interested in learning more about that, see [this article](https://ieeexplore.ieee.org/document/9825432).

## Initialization

```py
MyNetwork = Network(b1, b2, b3... # all nodes in the network
                    start=b1, # source node
                    end=bn,
                    generic_path=Path) # destination node

"""
The generic path is the standard path that data will take from the start node to the end node. This path can be used to compare how the reconfigured network improves over using a generic path as a function of the receiver power.

Path structure: [<Name>, <Name>, <Name>, <Name>...]
"""
```

## Methods

### MyNetwork.generate_messages(balloon, amt)

Generate random messages at a given balloon, with a certain amount.

### MyNetwork.calculate_total_rp(time, rp_calculator, path="Generic" or "Current")

Calculate the total end-to-end (E2E) receiver power for a given path. A path that looks like `[1, 2, 3, 4, 5]` means the start node (1) goes through nodes 2, 3, 4 before reaching the end node (5). The receiver power between each tx/rx pair is added to get the E2E receiver power. `rp_calculator` is a reference to a function that calculates receiver power.

### MyNetwork.recalculate(time, rp_calculator)

Recalculate the best contact graph at a given time. `rp_calculator` is a reference to a function that calculates receiver power. We populate this with `NetworkAnalyzer`'s `rp()` method.

### MyNetwork.transmit(time)

Transmit messages in accordance with the contact graph at a given time. This can be implemented along with the tick of the motion of a balloon (see [Balloon](./Balloon.md)).

### MyNetwork.add_obstacle(Obstacle)

Add an obstacle to the network. See the [Obstacle](/docs/Obstacle.md) page for more information.

## `Network` data

- `connections`: A dictionary containing all of the connected node pairs and their associated receiver power.
- `cg`: A Networkx weighted and directed graph.
- `message_queue`: A dictionary containing all of the messages located at all of the nodes in the network.
- `stored`: A list containing every time messages were stores because there was no path forward.
- `forwarded`: The number of messages forwarded between nodes.
- `THRESHOLD`: The minimum dB that qualifies a contact graph to be denoted as "significantly different" from the previous contact graph.
- `reconfigures`: A list containing every time that the contact graph was reconfigured.
- `start_node`: The node where all messages originate from.
- `end_node`: The node where all messages will end up.
- `path`: The current best (most inclusive) path between the source and destination.
- `path_weight`: The weight of the current path.
- `received_messages`: The number of messages successfully pulled from the destination.
- `sent_messages`: The number of messages successfully sent by the source.