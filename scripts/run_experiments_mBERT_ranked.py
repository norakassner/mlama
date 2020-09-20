# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
import argparse
from batch_eval_KB_completion_mBERT_ranked import main as run_evaluation
from batch_eval_KB_completion_mBERT_ranked import load_file
from lama.modules import build_model_by_name
import pprint
import statistics
from os import listdir
import os
from os.path import isfile, join
from shutil import copyfile
from collections import defaultdict
import json

LMs = [
    {
        "lm": "bert",
        "label": "mbert_base",
        "models_names": ["bert"],
        "bert_model_name": "bert-base-multilingual-cased",
        "bert_model_dir": None
    },
]


def run_experiments(
    relations,
    data_path_pre,
    data_path_post,
    language,
    input_param={
        "lm": "bert",
        "label": "bert_large",
        "models_names": ["bert"],
        "bert_model_name": "bert-large-cased",
        "bert_model_dir": "pre-trained_language_models/bert/cased_L-24_H-1024_A-16",
    },
):
    model = None
    pp = pprint.PrettyPrinter(width=41, compact=True)

    object_path = "/mounts/work/philipp/lama/data/TREx_multilingual/objects/" + language + ".json"
    with open(object_path) as f:
        candidates = json.load(f)

    for relation in relations:
        pp.pprint(relation)
        PARAMETERS = {
            "dataset_filename": "{}{}{}".format(
                data_path_pre, relation["relation"], data_path_post
            ),
            "common_vocab_filename": None,
            "template": "",
            "bert_vocab_name": "vocab.txt",
            "batch_size": 1,
            "logdir": "output",
            "full_logdir": "output/results/{}/{}/{}".format(
                input_param["label"], language, relation["relation"]
            ),
            "lowercase": False,
            "max_sentence_length": 100,
            "threads": -1,
            "interactive": False,
        }

        if "template" in relation:
            PARAMETERS["template"] = relation["template"]

        PARAMETERS.update(input_param)
        print(PARAMETERS)

        args = argparse.Namespace(**PARAMETERS)

        # see if file exists
        try:
            data = load_file(args.dataset_filename)
        except Exception as e:
            print("Relation {} excluded.".format(relation["relation"]))
            print("Exception: {}".format(e))
            continue

        if model is None:
            [model_type_name] = args.models_names
            model = build_model_by_name(model_type_name, args)

        max_length = 0
        dict_num_mask = {}
        for obj in candidates[relation["relation"]]["objects"]:
            if len(model.tokenizer.tokenize(obj)) > max_length:
                max_length = len(model.tokenizer.tokenize(obj))
        for l in range(1, max_length+1):
            dict_num_mask[l] = {}
        for obj in candidates[relation["relation"]]["objects"]:
            dict_num_mask[len(model.tokenizer.tokenize(obj))][obj] = model.get_id(obj)

        run_evaluation(args, max_length, dict_num_mask, shuffle_data=False, model=model)


def get_TREx_parameters(data_path_pre="data/"):
    relations = load_file("{}relations.jsonl".format(data_path_pre))
    data_path_pre += "TREx/"
    data_path_post = ".jsonl"
    return relations, data_path_pre, data_path_post


def get_GoogleRE_parameters():
    relations = [
        {
            "relation": "place_of_birth",
            "template": "[X] was born in [Y] .",
            "template_negated": "[X] was not born in [Y] .",
        },
        {
            "relation": "date_of_birth",
            "template": "[X] (born [Y]).",
            "template_negated": "[X] (not born [Y]).",
        },
        {
            "relation": "place_of_death",
            "template": "[X] died in [Y] .",
            "template_negated": "[X] did not die in [Y] .",
        },
    ]
    data_path_pre = "data/Google_RE/"
    data_path_post = "_test.jsonl"
    return relations, data_path_pre, data_path_post


def get_ConceptNet_parameters(data_path_pre="data/"):
    relations = [{"relation": "test"}]
    data_path_pre += "ConceptNet/"
    data_path_post = ".jsonl"
    return relations, data_path_pre, data_path_post


def get_Squad_parameters(data_path_pre="data/"):
    relations = [{"relation": "test"}]
    data_path_pre += "Squad/"
    data_path_post = ".jsonl"
    return relations, data_path_pre, data_path_post

def get_MultiLingual_parameters(data_path_pre="/mounts/work/philipp/lama/data/TREx_multilingual/", language=""):
    relations = load_file("{}templates/relations_{}.jsonl".format(data_path_pre, language))
    data_path_pre += language + "/"
    data_path_post = ".jsonl"
    return relations, data_path_pre, data_path_post, language


def get_MultiLingual_parameters_GoogleRe(data_path_pre="/mounts/work/philipp/lama/data/Google_RE_multilingual/", language=""):
    relations = load_file("{}templates/relations_{}.jsonl".format(data_path_pre, language))
    data_path_pre += language + "/"
    data_path_post = "_test.jsonl"
    return relations, data_path_pre, data_path_post, language


def run_all_LMs(parameters):
    for ip in LMs:
        print(ip["label"])
        run_experiments(*parameters, input_param=ip)


if __name__ == "__main__":

    languages = []
    with open("languages.txt", "r") as f:
        for line in f:
            languages.append(line.strip())

    print("Multilingual")
    languages = ["en"]
    for l in languages:
       parameters = get_MultiLingual_parameters(language=l)
       run_all_LMs(parameters)
