# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
from lama.modules import build_model_by_name
import lama.utils as utils
from lama.utils import print_sentence_predictions, load_vocab
import lama.options as options
from tqdm import tqdm
from random import shuffle
import os
import json
import spacy
import lama.modules.base_connector as base
from pprint import pprint
import logging.config
import logging
import pickle
from multiprocessing.pool import ThreadPool
import multiprocessing
import lama.evaluation_metrics_ranked as metrics
import time, sys


def load_file(filename):
    data = []
    with open(filename, "r") as f:
        for line in f.readlines():
            data.append(json.loads(line))
    return data


def create_logdir_with_timestamp(base_logdir, modelname):
    timestr = time.strftime("%Y%m%d_%H%M%S")

    # create new directory
    log_directory = "{}/{}_{}/".format(base_logdir, modelname, timestr)
    os.makedirs(log_directory)

    path = "{}/last".format(base_logdir)
    try:
        os.unlink(path)
    except Exception:
        pass
    os.symlink(log_directory, path)
    return log_directory


def parse_template(template, subject_label, object_label):
    SUBJ_SYMBOL = "[X]"
    OBJ_SYMBOL = "[Y]"
    template = template.replace(SUBJ_SYMBOL, subject_label)
    template = template.replace(OBJ_SYMBOL, object_label)
    return [template]


def init_logging(log_directory):
    logger = logging.getLogger("LAMA")
    logger.setLevel(logging.DEBUG)

    os.makedirs(log_directory, exist_ok=True)

    # logging format
    # "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # file handler
    fh = logging.FileHandler(str(log_directory) + "/info.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.propagate = False

    return logger


def batchify(data, batch_size):
    msg = ""
    list_samples_batches = []
    list_sentences_batches = []
    current_samples_batch = []
    current_sentences_batches = []
    c = 0

    # sort to group togheter sentences with similar length
    for sample in sorted(
        data, key=lambda k: len(" ".join(k["masked_sentences"]).split())
    ):
        masked_sentences = sample["masked_sentences"]
        current_samples_batch.append(sample)
        current_sentences_batches.append(masked_sentences)
        c += 1
        if c >= batch_size:
            list_samples_batches.append(current_samples_batch)
            list_sentences_batches.append(current_sentences_batches)
            current_samples_batch = []
            current_sentences_batches = []
            c = 0

    # last batch
    if current_samples_batch and len(current_samples_batch) > 0:
        list_samples_batches.append(current_samples_batch)
        list_sentences_batches.append(current_sentences_batches)

    return list_samples_batches, list_sentences_batches, msg


def run_thread(arguments):

    msg = ""

    # 1. compute the ranking metrics on the filtered log_probs tensor
    experiment_result, return_msg = metrics.get_ranking(
        arguments["filtered_log_probs"],
        arguments["sample"],
        arguments["masked_indices"],
        arguments["vocab"],
        arguments["candidates"],
        label_index=arguments["label_index"],
        index_list=arguments["index_list"],
        print_generation=arguments["interactive"],
        topk=100,
    )
    msg += "\n" + return_msg

    return experiment_result, msg


def lowercase_samples(samples, use_negated_probes=False):
    new_samples = []
    for sample in samples:
        sample["obj_label"] = sample["obj_label"].lower()
        sample["sub_label"] = sample["sub_label"].lower()
        lower_masked_sentences = []
        for sentence in sample["masked_sentences"]:
            sentence = sentence.lower()
            sentence = sentence.replace(base.MASK.lower(), base.MASK)
            lower_masked_sentences.append(sentence)
        sample["masked_sentences"] = lower_masked_sentences

        new_samples.append(sample)
    return new_samples


def filter_samples(model, samples, vocab_subset, max_sentence_length, template):
    msg = ""
    new_samples = []
    samples_exluded = 0
    for sample in samples:
        excluded = False
        if "obj_label" in sample and "sub_label" in sample:

            obj_label_ids = model.get_id(sample["obj_label"])

            if obj_label_ids:
                recostructed_word = " ".join(
                    [model.vocab[x] for x in obj_label_ids]
                ).strip()
            else:
                recostructed_word = None

            excluded = False
            if not template or len(template) == 0:
                masked_sentences = sample["masked_sentences"]
                text = " ".join(masked_sentences)
                if len(text.split()) > max_sentence_length:
                    msg += "\tEXCLUDED for exeeding max sentence length: {}\n".format(
                        masked_sentences
                    )
                    samples_exluded += 1
                    excluded = True
            if sample['from_english']:
                msg += "\tEXCLUDED not in language \n"
                excluded = True
                samples_exluded += 1
            # MAKE SURE THAT obj_label IS IN VOCABULARIES
            if vocab_subset:
                for x in sample["obj_label"].split(" "):
                    if x not in vocab_subset:
                        excluded = True
                        msg += "\tEXCLUDED object label {} not in vocab subset\n".format(
                            sample["obj_label"]
                        )
                        samples_exluded += 1
                        break
            if excluded:
                pass
            elif obj_label_ids is None:
                msg += "\tEXCLUDED object label is {} None\n".format(
                    sample["obj_label"]
                )
                samples_exluded += 1

            #   samples_exluded+=1
            elif "judgments" in sample:
                # only for Google-RE
                num_no = 0
                num_yes = 0
                for x in sample["judgments"]:
                    if x["judgment"] == "yes":
                        num_yes += 1
                    else:
                        num_no += 1
                if num_no > num_yes:
                    # SKIP NEGATIVE EVIDENCE
                    pass
                else:
                    new_samples.append(sample)
            else:
                new_samples.append(sample)
        else:
            msg += "\tEXCLUDED since 'obj_label' not sample or 'sub_label' not in sample: {}\n".format(
                sample
            )
            samples_exluded += 1
    msg += "samples exluded  : {}\n".format(samples_exluded)
    return new_samples, msg


def main(args, NUM_MASK, candidates, shuffle_data=True, model=None):

    if len(args.models_names) > 1:
        raise ValueError('Please specify a single language model (e.g., --lm "bert").')

    msg = ""

    [model_type_name] = args.models_names

    print(model)
    if model is None:
        model = build_model_by_name(model_type_name, args)

    if model_type_name == "fairseq":
        model_name = "fairseq_{}".format(args.fairseq_model_name)
    elif model_type_name == "bert":
        model_name = "BERT_{}".format(args.bert_model_name)
    elif model_type_name == "elmo":
        model_name = "ELMo_{}".format(args.elmo_model_name)
    else:
        model_name = model_type_name.title()

    # initialize logging
    if args.full_logdir:
        log_directory = args.full_logdir
    else:
        log_directory = create_logdir_with_timestamp(args.logdir, model_name)
    logger = init_logging(log_directory)
    msg += "model name: {}\n".format(model_name)

    # deal with vocab subset
    vocab_subset = None
    index_list = None
    msg += "args: {}\n".format(args)
    if args.common_vocab_filename is not None:
        vocab_subset = load_vocab(args.common_vocab_filename)
        msg += "common vocabulary size: {}\n".format(len(vocab_subset))

        # optimization for some LM (such as ELMo)
        model.optimize_top_layer(vocab_subset)

        filter_logprob_indices, index_list = model.init_indices_for_filter_logprobs(
            vocab_subset, logger
        )

    logger.info("\n" + msg + "\n")

    # dump arguments on file for log
    with open("{}/args.json".format(log_directory), "w") as outfile:
        json.dump(vars(args), outfile)

    data = load_file(args.dataset_filename)

    if args.lowercase:
        # lowercase all samples
        logger.info("lowercasing all samples...")
        all_samples = lowercase_samples(
            data, use_negated_probes=args.use_negated_probes
        )
    else:
        # keep samples as they are
        all_samples = data


    # create uuid if not present
    i = 0
    for sample in all_samples:
        sample["uuid"] = i
        i += 1




    all_samples, ret_msg = filter_samples(
        model, data, vocab_subset, args.max_sentence_length, args.template
    )

    # OUT_FILENAME = "{}.jsonl".format(args.dataset_filename)
    # with open(OUT_FILENAME, 'w') as outfile:
    #     for entry in all_samples:
    #         json.dump(entry, outfile)
    #         outfile.write('\n')

    logger.info("\n" + ret_msg + "\n")


    # if template is active (1) use a single example for (sub,obj) and (2) ...
    if args.template and args.template != "":
        facts = []
        for sample in all_samples:
            sub = sample["sub_label"]
            obj = sample["obj_label"]
            uuid = sample["uuid"]
            if (sub, obj, uuid) not in facts:
                facts.append((sub, obj, uuid))
        local_msg = "distinct template facts: {}".format(len(facts))
        logger.info("\n" + local_msg + "\n")
        print(local_msg)
        all_samples = []
        for fact in facts:
            (sub, obj, uuid) = fact
            sample = {}
            sample["sub_label"] = sub
            sample["obj_label"] = obj
            sample["uuid"] = uuid
            # sobstitute all sentences with a standard template
            sample["masked_sentences"] = parse_template(
                args.template.strip(), sample["sub_label"].strip(), base.MASK
            )

            all_samples.append(sample)

    # shuffle data
    if shuffle_data:
        shuffle(all_samples)

    samples_batches, sentences_batches, ret_msg = batchify(all_samples, args.batch_size)
    logger.info("\n" + ret_msg + "\n")

    # ThreadPool
    num_threads = args.threads
    if num_threads <= 0:
        # use all available threads
        num_threads = multiprocessing.cpu_count()
    pool = ThreadPool(num_threads)
    list_of_results = []

    for i in tqdm(range(len(samples_batches))):

        samples_b = samples_batches[i]
        # sentences_b = sentences_batches[i]
        masked_sentences = []
        sentences_b = []
        for num_mask in range(1, NUM_MASK+1):
            for sentence in samples_b[0]["masked_sentences"]:
                sentence = sentence.replace(base.MASK, (base.MASK)*num_mask)
                sentence = sentence.replace("][", "] [")
                masked_sentences.append(sentence)
                sentences_b.append([sentence])
        samples_b[0]["masked_sentences"] = masked_sentences

        (
            original_log_probs_list,
            token_ids_list,
            masked_indices_list,
        ) = model.get_batch_generation(sentences_b, logger=logger)

        if vocab_subset is not None:
            # filter log_probs
            filtered_log_probs_list = model.filter_logprobs(
                original_log_probs_list, filter_logprob_indices
            )
        else:
            filtered_log_probs_list = original_log_probs_list

        label_index_list = []
        for sample in samples_b:
            obj_label_id = model.get_id(sample["obj_label"])

            # MAKE SURE THAT obj_label IS IN VOCABULARIES
            if obj_label_id is None:
                raise ValueError(
                    "object label id {} is None".format(
                        sample["obj_label"]
                    )
                )

            label_index_list.append(obj_label_id)

        arguments = [
            {
                "original_log_probs": original_log_probs_list,
                "filtered_log_probs": filtered_log_probs_list,
                "token_ids": token_ids_list[0],
                "vocab": model.vocab,
                "label_index": label_index_list[0],
                "masked_indices": masked_indices_list,
                "interactive": args.interactive,
                "index_list": index_list,
                "sample": sample,
                "candidates": candidates,
            }
            for sample in zip(
                samples_b,
            )
        ]

        # multithread
        res = pool.map(run_thread, arguments)

        for idx, result in enumerate(res):

            result_masked_topk, msg = result

            logger.info("\n" + msg + "\n")

            sample = samples_b[idx]

            element = {}
            element["sample"] = sample
            element["uuid"] = sample["uuid"]
            element["token_ids"] = token_ids_list[0]
            element["masked_indices"] = masked_indices_list[0]
            element["label_index"] = label_index_list[0]
            element["masked_topk"] = result_masked_topk

            list_of_results.append(element)

    pool.close()
    pool.join()

    # dump pickle with the result of the experiment
    all_results = dict(
        list_of_results=list_of_results
    )
    with open("{}/result.pkl".format(log_directory), "wb") as f:
        pickle.dump(all_results, f)


if __name__ == "__main__":
    parser = options.get_eval_KB_completion_parser()
    args = options.parse_args(parser)
    main(args)
