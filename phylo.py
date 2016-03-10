#!/usr/bin/env python
from __future__ import print_function

import json
import os

from dammit.fileio import maf
import numpy as np
import pandas as pd
import pyprind
from skbio import TreeNode


def skbio_json_converter(tree):
    json_obj = {}
    json_obj['taxid'] = tree.name
    json_obj['organism'] = unicode(tree.organism, "ISO-8859-1") if hasattr(tree, 'organism') else json_obj['taxid']

    if hasattr(tree, 'children'):
        json_obj['children'] = [ json_converter(c) for c in tree.children ]
    return json_obj


def skbio_write_json(tree, filename):
    json_rep = json_converter(tree)
    with open(filename, 'wb') as fp:
        json.dump(json_rep, fp)


def load_odb_alignments(filename):
    # load up the OrthoDB MAF alignment file from LAST
    odb_hits_df = pd.concat(maf.MafParser(filename))
    # calculate P values from E values
    odb_hits_df['P_not_fp'] = np.exp(-odb_hits_df.EG2)

    return odb_hits_df


def load_odb_taxid_map(filename, ncbi_rename_filename):
    # Get the (OrthoDB<->NCBI Taxonomy ID) mapping
    df = pd.read_csv(filename)
    with open(ncbi_rename_filename) as fp:
        ncbi_rename_map = json.load(fp)
    df['taxid'] = df.taxid.apply(lambda tx: ncbi_rename_map.get(tx, tx))
    return df


def load_odb_base_tree(tree_filename):
    odb_tree = TreeNode.read(tree_filename)
    odb_tree_index = {}

    odb_tree.name = 'root'
    for node in odb_tree.postorder():
        node.name = int(node.name) if node.name != 'root' else node.name
        odb_tree_index[node.name] = node

    return odb_tree, odb_tree_index


def transfer_probs(subtree):
    if subtree.is_tip():
        subtree.Probs.append(subtree.current_p)
        #subtree.current_p = 0.0
        return subtree.Probs[-1:]
    else:
        child_probs = []
        for child in subtree.children:
            child_probs.extend(transfer_probs(child))
        # if we had branch distances we would divide by sum(distances), but for now dist always equals 1
        if not child_probs:
            avg_prob = 0.0
        else:
            avg_prob = np.mean(child_probs)

        subtree.Probs.append(avg_prob)
        child_probs.append(avg_prob)

        if not subtree.is_root():
            return child_probs
        else:
            pass


def set_current_p(row, tree_index):
    taxid = row.taxid
    try:
        tree_index[taxid].current_p = row.P_not_fp
    except KeyError as e:
        if np.isnan(taxid): # figure out wtf is happening here
            return
    try:
        tree_index[taxid].current_p = row.P_not_fp
    except KeyError as e:
        #print(e)
        pass


def reset_tree_probs(tree):
    for node in tree.postorder():
        setattr(node, 'Probs', [])
        setattr(node, 'current_p', 0.0)


def reset_tree_current_p(tree):
    for node in tree.postorder():
        setattr(node, 'current_p', 0.0)


def calculate_avg_probs(tree):
    for node in tree.postorder():
        node.P = np.mean(node.Probs)


def calculate_clade_probs(tree, tree_index, hits_df):

    reset_tree_probs(tree)

    bar = pyprind.ProgBar(len(hits_df.q_name.unique()),
                          title='Calculating probability masses.',
                          width=80, monitor=True)

    # for each transcript, accumulate probability mass
    for transcript, group in hits_df.groupby('q_name'):
        # for now we just choose the best hit of their are multiple hits per subject
        group = group.sort_values(['s_name', 'P_not_fp'], ascending=False).drop_duplicates(subset='s_name')
        reset_tree_current_p(tree)
        group.apply(set_current_p, args=(tree_index,), axis=1)
        transfer_probs(tree)
        bar.update(item_id = '{0} (with {1} hits)'.format(transcript, len(group)))

    calculate_avg_probs(tree)

    probs = {node.name:node.P for node in tree.postorder()}
    return probs


def analyze(args):

    def get_filename(filename):
        return os.path.join(args.database_dir,
                            filename)

    odb_taxid_df = load_odb_taxid_map(get_filename('odb8_taxid_map.csv'),
                                      get_filename('ncbi_taxid_rename.json'))

    # Load up the base OrthoDB tree
    odb_tree, odb_tree_index = load_odb_base_tree(get_filename('odb8_base_tree.nwk'))

    odb_hits_df = pd.merge(load_odb_alignments(args.alignments),
                           odb_taxid_df.reset_index(),
                           left_on='s_name',
                           right_on='protein_id',
                           how='left')

    probs = calculate_clade_probs(odb_tree, odb_tree_index, odb_hits_df)
    with open(args.results, 'wb') as fp:
        json.dump(probs, fp)
