# -*- coding: UTF-8 -*-

"""Generate a GEXF (Graph Exchange XML Format) file for the message network of
the Iron March forum.
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

from collections import Counter
import pickle

import numpy as np
import networkx as nx
import pandas as pd

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# CSV files for message, topic, and post data
INPUT_MESSAGE_CSV = '../csv/core_message_posts.csv'
INPUT_TOPIC_CSV = '../csv/core_message_topics.csv'
INPUT_POSTS_CSV = '../csv/forums_posts.csv'

# file to save Pandas DataFrame of edges to
OUTPUT_EDGES_DF = '../output/message_edges.df'

# file to save GEXF file to
OUTPUT_GEXF = '../output/messages.gexf'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # read CSV files for messages and optics into Pandas DataFrames
  #---------------------------------------------------------------------------#

  mdf = pd.read_csv( INPUT_MESSAGE_CSV )
  tdf = pd.read_csv( INPUT_TOPIC_CSV )
  fdf = pd.read_csv( INPUT_POSTS_CSV )

  # 1. Extract edges
  #############################################################################

  # initialize dict of edges, where keys are tuples of users and values are
  # number of messages exchanged.
  edges_dict = dict()

  # loop over all conversations (message topic IDs)
  for msg_id in tdf['mt_id']:

    # extract conversation information from `core_message_posts` dataset
    #.........................................................................#

    # create temporary DataFrame for all messages in a given conversation, from
    # `core_message_posts` dataset
    tmpdf = mdf[mdf['msg_topic_id'] == msg_id]

    # generate list of all unique users in the given conversation, from
    # `core_message_posts` dataset
    users_m = list(set(tmpdf['msg_author_id']))

    # extract conversation information from `core_message_topics` dataset
    #.........................................................................#

    # create temporary DataFrame for all messages in a given conversation, from
    # `core_message_topics` dataset. This is necessary because neither dataset
    # contains all message information: `core_message_topics` has null values
    # for column `mt_to_member_id` after line 2994.
    tmpdf = tdf[tdf['mt_id'] == msg_id]

    # generate list of all unique users in the given conversation, from
    # `core_message_topics` dataset
    users_t = [int(tmpdf['mt_starter_id']), int(tmpdf['mt_to_member_id'] ) ]

    # for a given conversation, combine lists of participants, from both
    # datasets
    users = list(set(users_m + users_t))

    # calculate number of replies for given dataset
    replies = int(tmpdf['mt_replies'])

    # remove null values from list of conversation participants
    if 0 in users:
      users.remove(0)

    # convery list of conversation participants to tuple (dict keys must be
    # hashable: lists are not hashable but tuples are). Tuple is sorted to
    # guarantee uniqueness and avoid double-counting conversations
    users = tuple(sorted(users))

    # remove all conversations that don't have 2 participants, for simplify
    if len(users) != 2:
      pass
    # remove all conversations with less than 3 replies, to avoid overly
    # cluttered visualization
    elif replies < 3:
      pass
    else:
      if users not in edges_dict:
        # conversation hasn't been previously stored in `edges_dict : create
        # new entry`
        edges_dict[users] = replies
      else:
        # conversation has been previously stored in `edges_dict`: update entry
        edges_dict[users] += replies

  # convert values in `edges_dict` to two NumPy arrays
  edges_arr = np.asarray(list(edges_dict.keys()))
  weights_arr = np.asarray(list(edges_dict.values()))

  # store edge information in a Pandas DataFrame
  edges_df = pd.DataFrame()
  edges_df['source'] = edges_arr[:, 0]
  edges_df['target'] = edges_arr[:, 1]
  edges_df['weight'] = weights_arr

  # write `edges_df` to file
  edges_df.to_pickle( OUTPUT_EDGES_DF )

  # 2. Extract nodes
  #############################################################################

  # extract list of unique nodes (i.e. forum users that participated in a
  # conversation) and convert user index from int to string
  nodes_list = list(set(edges_arr.flatten()))
  nodes_list = [str(node) for node in nodes_list]

  # 3. Prepare graph
  #############################################################################

  # compute base-10 logarithm of number of posts, to be used for radius of node
  # circles
  #---------------------------------------------------------------------------#

  node_size = dict()
  for node in nodes_list:
    node_size[node] = np.log10( np.sum(fdf['author_id'] == int(node)) + 1)

  # create list of edge bundles for NetworkX
  #---------------------------------------------------------------------------#

  # initialize empty list of edge bundles
  edges_list = [ ]

  # loop over edges
  for i in range(edges_df.shape[0]):

    # create temporary DataFrame for a given edge
    _tmpdf = edges_df.loc[i]

    # extract information about edge
    usr_from = _tmpdf['source']
    usr_to = _tmpdf['target']
    weight = np.log10(_tmpdf['weight'] + 1)

    # create edge bundle
    bundle = (str(usr_to), str(usr_from), {'weight' : weight } )

    # add bundle to edge bundle list
    edges_list.append(bundle)

  # 4. Create and save graph
  #############################################################################

  # initialize NetworkX graph
  G = nx.Graph()

  # add list of odes to graph
  G.add_nodes_from( nodes_list )

  # add list of edge bundles to graph
  G.add_edges_from( edges_list )

  # add graph attribute for log of number of posts
  nx.set_node_attributes(G, node_size, 'log_posts')

  # write GEXF to file
  nx.write_gexf( G, OUTPUT_GEXF )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#