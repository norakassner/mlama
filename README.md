# mLAMA: multilingual LAnguage Model Analysis

This repository contains code for the EACL 2021 paper ["Multilingual LAMA: Investigating Knowledge in Multilingual Pretrained Language Models"](xxx).
It extends the original LAMA probe to the multilingual setting, e.g. it probes knowledge in pre-trained language models in a multilingual setting.

The repository is forked from https://github.com/facebookresearch/LAMA and adapted accordingly. 

## The mLAMA probe

To reproduce our results:

### 1. Create conda environment and install requirements

(optional) It might be a good idea to use a separate conda environment. It can be created by running:
```
conda create -n mlama -y python=3.7 && conda activate mlama
pip install -r requirements.txt
```

add project to path:

export PYTHONPATH=${PYTHONPATH}:/path-to-project

### 2. Download the data


```bash
wget http://cistern.cis.lmu.de/mlama/mlama.zip
unzip mlama.zip
rm data.zip
```

### 3. Run the experiments

```bash
python scripts/run_experiments_mBERT_ranked.py 
python scripts/eval.py
```

## The dataset

Code to recreate the dataset can be found in the folder `dataset`. 

We provide a class to read in the dataset in `dataset/reader.py`. Example for reading the data: 
```python
ml = MLama("data/mlama/")
ml.load()
```

## Reference:

The original LAMA probe is described in the following paper:

```bibtex
@inproceedings{kassner2021multilingual,
    title = "Multilingual {LAMA}: Investigating Knowledge in Multilingual Pretrained Language Models",
    author = {Kassner, Nora  and
      Dufter, Philipp  and
      Sch{\"u}tze, Hinrich},
    booktitle = "to appear in Proceedings of he 16th Conference of the European Chapter of the Association for Computational Linguistics",
    year = "2021",
    address = "Online",
    publisher = "Association for Computational Linguistics",
}

@inproceedings{petroni2019language,
  title={Language Models as Knowledge Bases?},
  author={F. Petroni, T. Rockt{\"{a}}schel, A. H. Miller, P. Lewis, A. Bakhtin, Y. Wu and S. Riedel},
  booktitle={In: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2019},
  year={2019}
}
```

## Acknowledgements

* [https://github.com/huggingface/pytorch-pretrained-BERT](https://github.com/huggingface/pytorch-pretrained-BERT)
* [https://github.com/allenai/allennlp](https://github.com/allenai/allennlp)
* [https://github.com/pytorch/fairseq](https://github.com/pytorch/fairseq)
* https://github.com/facebookresearch/LAMA
