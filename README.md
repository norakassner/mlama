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

It is forked from https://github.com/facebookresearch/LAMA and adapted accordingly. 
## Reference:

The LAMA probe is described in the following papers:

```bibtex
@inproceedings{petroni2019language,
  title={Language Models as Knowledge Bases?},
  author={F. Petroni, T. Rockt{\"{a}}schel, A. H. Miller, P. Lewis, A. Bakhtin, Y. Wu and S. Riedel},
  booktitle={In: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2019},
  year={2019}
}

@inproceedings{petroni2020how,
  title={How Context Affects Language Models' Factual Predictions},
  author={Fabio Petroni and Patrick Lewis and Aleksandra Piktus and Tim Rockt{\"a}schel and Yuxiang Wu and Alexander H. Miller and Sebastian Riedel},
  booktitle={Automated Knowledge Base Construction},
  year={2020},
  url={https://openreview.net/forum?id=025X0zPfn}
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

### 3. Download the models

#### DISCLAIMER: ~55 GB on disk

Install spacy model
```bash
python3 -m spacy download en
```

Download the models
```bash
chmod +x download_models.sh
./download_models.sh
```

The script will create and populate a _pre-trained_language_models_ folder.
If you are interested in a particular model please edit the script.


### 4. Run the experiments

```bash
python scripts/run_experiments_mBERT_ranked.py 
python eval/mBERT_ranked.py
```
## Acknowledgements

* [https://github.com/huggingface/pytorch-pretrained-BERT](https://github.com/huggingface/pytorch-pretrained-BERT)
* [https://github.com/allenai/allennlp](https://github.com/allenai/allennlp)
* [https://github.com/pytorch/fairseq](https://github.com/pytorch/fairseq)


## Other References

- __(Kassner et al., 2019)__ Nora Kassner, Hinrich Schütze. _Negated LAMA: Birds cannot fly_. arXiv preprint arXiv:1911.03343, 2019.

- __(Poerner et al., 2019)__ Nina Poerner, Ulli Waltinger, and Hinrich Schütze. _BERT is Not a Knowledge Base (Yet): Factual Knowledge vs. Name-Based Reasoning in Unsupervised QA_. arXiv preprint arXiv:1911.03681, 2019.

- __(Dai et al., 2019)__ Zihang Dai, Zhilin Yang, Yiming Yang, Jaime G. Carbonell, Quoc V. Le, and Ruslan Salakhutdi. _Transformer-xl: Attentive language models beyond a fixed-length context_. CoRR, abs/1901.02860.

- __(Peters et al., 2018)__ Matthew E. Peters, Mark Neumann, Mohit Iyyer, Matt Gardner, Christopher Clark, Kenton Lee, and Luke Zettlemoyer. 2018. _Deep contextualized word representations_. NAACL-HLT 2018

- __(Devlin et al., 2018)__ Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2018. _BERT: pre-training of deep bidirectional transformers for language understanding_. CoRR, abs/1810.04805.

- __(Radford et al., 2018)__ Alec Radford, Karthik Narasimhan, Tim Salimans, and Ilya Sutskever. 2018. _Improving language understanding by generative pre-training_.

- __(Liu et al., 2019)__ Yinhan Liu, Myle Ott, Naman Goyal, Jingfei Du, Mandar Joshi, Danqi Chen, Omer Levy, Mike Lewis, Luke Zettlemoyer, Veselin Stoyanov. 2019. _RoBERTa: A Robustly Optimized BERT Pretraining Approach_. arXiv preprint arXiv:1907.11692.

