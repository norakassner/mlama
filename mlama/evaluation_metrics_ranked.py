# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
import torch
import numpy as np
import scipy


def __max_probs_values_indices(masked_indices, log_probs, topk=1000):

    masked_index = masked_indices

    objects = candidates[len(masked_index)]

    log_probs = log_probs[masked_index]

    value_max_probs, index_max_probs = torch.topk(input=log_probs,k=topk,dim=1)
    index_max_probs = index_max_probs.numpy().astype(int)
    value_max_probs = value_max_probs.detach().numpy()

    return log_probs, index_max_probs, value_max_probs


def __print_top_k(value_max_probs, index_max_probs, vocab, mask_topk, index_list, candidates_obj, max_printouts = 10):
    result = []
    msg = "\n| Top{} predictions\n".format(max_printouts)
    for i in range(mask_topk):
        idx_joined = []
        word_form_joined = []

        for n_mask in range(len(value_max_probs)):
            filtered_idx = index_max_probs[n_mask][i].item()

            if index_list is not None:
                # the softmax layer has been filtered using the vocab_subset
                # the original idx should be retrieved
                idx = index_list[filtered_idx]
            else:
                idx = filtered_idx

            log_prob = value_max_probs[n_mask][i].item()
            word_form = vocab[idx]

            word_form_joined.append(word_form)
            idx_joined.append(idx)
            if i < max_printouts:
                msg += "{:<8d}{:<20s}{:<12.3f}\n".format(
                    i,
                    word_form,
                    log_prob
                )
        element = {'i' : i, 'token_idx': idx_joined, 'log_prob': log_prob, 'token_word_form': word_form_joined}
        result.append(element)
    return result, msg

def get_prediction(log_probs, masked_indices, vocab, label_index = None, index_list = None, topk = 1000, P_AT = 10, print_generation=True):

    experiment_result = {}

    # score only first mask
    masked_indices = masked_indices[:1]

    masked_index = masked_indices[0]
    log_probs = log_probs[masked_index]

    value_max_probs, index_max_probs = torch.topk(input=log_probs,k=topk,dim=0)
    index_max_probs = index_max_probs.numpy().astype(int)
    value_max_probs = value_max_probs.detach().numpy()

    result_masked_topk, return_msg = __print_top_k(value_max_probs, index_max_probs, vocab, topk, index_list)

    return result_masked_topk, return_msg


def get_ranking(log_probs, sample, masked_indices, vocab, candidates, label_index = None, index_list = None, topk = 10, P_AT = 10, print_generation=True):
    experiment_result = {}
    dict_probs = {}
    return_msg = ""
    objects_true = sample["obj_label"]

    for i, num_masks in enumerate(candidates):
        if len(masked_indices) >1:
            masked_idx = masked_indices[i]
        else:
            masked_idx = [masked_indices[i]]
        predictions = log_probs[i][masked_idx]

        for object in candidates[num_masks]:
            probs = []
            for id, prediction in zip(candidates[num_masks][object], predictions):
                #print(id)
                #print("pred", prediction)
                probs.append(prediction[id])
            dict_probs[object] = np.mean(probs)
    object_keys = np.array(list(dict_probs.keys()))
    object_values = np.array(list(dict_probs.values()))
 
    idx_true = np.argwhere(objects_true == object_keys)[0][0]
    idcs = np.argsort(object_values)
    rank = len(object_values) - np.argwhere(idcs==idx_true)[0][0]

    experiment_result["rank"] = rank - 1
    experiment_result["prob_true"] = dict_probs[objects_true]
    experiment_result["predicted"] = object_keys[idcs]
    experiment_result["probs"] = object_values[idcs]

    return experiment_result, return_msg
