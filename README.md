# mLAMA: multilingual LAnguage Model Analysis

This repository contains code for the EACL 2021 paper:

```bibtex
@inproceedings{petroni2019language,
  title={Language Models as Knowledge Bases?},
  author={F. Petroni, T. Rockt{\"{a}}schel, A. H. Miller, P. Lewis, A. Bakhtin, Y. Wu and S. Riedel},
  booktitle={In: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2019},
  year={2019}
}
```
It extends the original LAMA probe to the multilingual setting, e.g. it probes knowledge in pre-trained language models in a multilingual setting.

The repository is forked from https://github.com/facebookresearch/LAMA and adapted accordingly. 

## Reference:

The original LAMA probe is described in the following paper:

```bibtex
@inproceedings{petroni2019language,
  title={Language Models as Knowledge Bases?},
  author={F. Petroni, T. Rockt{\"{a}}schel, A. H. Miller, P. Lewis, A. Bakhtin, Y. Wu and S. Riedel},
  booktitle={In: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2019},
  year={2019}
}
```

## The LAMA probe

To reproduce our results:

### 1. Create conda environment and install requirements

(optional) It might be a good idea to use a separate conda environment. It can be created by running:
```
conda create -n lama37 -y python=3.7 && conda activate lama37
pip install -r requirements.txt
```

add project to path:

export PYTHONPATH=${PYTHONPATH}:/path-to-project

### 2. Download the data

```bash
wget https://dl.fbaipublicfiles.com/LAMA/data.zip
unzip data.zip
rm data.zip
```

### 3. Run the experiments

```bash
python scripts/run_experiments_mBERT_ranked.py 
python eval/mBERT_ranked.py
```
## Acknowledgements

* [https://github.com/huggingface/pytorch-pretrained-BERT](https://github.com/huggingface/pytorch-pretrained-BERT)
* [https://github.com/allenai/allennlp](https://github.com/allenai/allennlp)
* [https://github.com/pytorch/fairseq](https://github.com/pytorch/fairseq)
* https://github.com/facebookresearch/LAMA
