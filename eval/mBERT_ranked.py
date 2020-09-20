import pickle
import os
import numpy as np

problem = []
f_out = open("output/mbert_ranked.csv", "w")
output_path = "output/results/mbert_base/"
languages = list(os.walk(output_path))[0][1:-1][0]
dict_languages_total = {}
dict_languages_P = {}

for lang in languages:
  print(lang)
  P_all = []
  P_all_eng = []
  total_all = []
  relations = list(os.walk(output_path + lang + "/"))[0][1:-1][0]

  for relation in relations:
       P = 0.0
       P_eng = 0.0
       total = 0.0

       with open(output_path + lang + "/" +  relation + "/" + 'result.pkl', 'rb') as f:
            data = pickle.load(f)
       with open("output/results/mbert_base/en/" +  relation + "/" + 'result.pkl', 'rb') as f:
            data_eng = pickle.load(f)

       eng_dict = {}
       for d in data_eng["list_of_results"]:
           rank = 0.0
           if d['masked_topk']["rank"]==0:
               rank = 1.0
           eng_dict[d["sample"]["uuid"]] = [rank, d["sample"]]
       for d in data["list_of_results"]:
           rank = 0.0
           if d['masked_topk']["rank"]==0:
               rank = 1.0
           P += rank
           total += 1.0
           idx = int(d["sample"]["uuid"])
           P_eng += eng_dict[idx][0]

       P_all.append(P/total)
       P_all_eng.append(P_eng/total)
       total_all.append(total)

  f_out.write(lang)
  f_out.write(",")
  f_out.write(str(np.sum(total_all)))
  f_out.write(",")
  f_out.write(str(np.mean(P_all)))
  f_out.write(",")
  f_out.write(str(np.mean(P_all_eng)))
  f_out.write("\n")

f_out.close()
