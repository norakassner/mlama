import argparse
from typing import Text, Dict, Set, Any
import json
import requests
import os
from tqdm import tqdm
from utils import get_logger, load_languagemapping

LOG = get_logger(__name__)





def translate(kgids: Set[Text], targetlang: Text, key: Text) -> Dict[Text, Text]:
    translations = {}
    kgids = list(kgids)
    kgids = [x for x in kgids if x.startswith("/m/")]
    batch_size = 16
    for i in tqdm(range(0, len(kgids), batch_size)): 
        response = requests.get("https://kgsearch.googleapis.com/v1/entities:search", {"key": key, "languages": targetlang, "ids": kgids[i:i + batch_size]})
        if response.status_code == 200:
            result = json.loads(response.content)
            for elem in result['itemListElement']:
                kgid = elem["result"]["@id"].replace("kg:", "")
                name = elem["result"]["name"]
                translations[kgid] = name
        else:
            LOG.warning("Wrong status code: {}".format(response))
            break
    return translations


def get_translation(current_id: Text, translations: Dict[Text, Text], triple: Dict[Text, Any]) -> Dict[Text, Any]:
    if current_id.startswith("/m/"):
        if current_id in translations:
            sub_translated = translations[current_id]
        else:
            sub_translated = None
    else:
        if triple["sub"] != triple["sub_label"]:
            sub_translated = None
        else:
            sub_translated = triple["sub"]
    return sub_translated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputpath", default=None, type=str, required=True, help="")
    parser.add_argument("--relation", default=None, type=str, required=True, help="")
    parser.add_argument("--outpath", default=None, type=str, required=True, help="")
    parser.add_argument("--languagemapping", default=None, type=str, required=True, help="")
    args = parser.parse_args()
    key = os.environ["GOOGLEAPIKEY"]
    lang2translateid = load_languagemapping(args.languagemapping)
    triples = []
    with open(os.path.join(args.inputpath, args.relation + ".jsonl")) as fp:
        for line in fp:
            if line.strip():
                triples.append(json.loads(line))

    kgids = set()
    for triple in triples:
        if "sub" in triple:
            kgids.add(triple["sub"])
        if "obj" in triple:
            kgids.add(triple["obj"])

    for langid, googleid in lang2translateid.items():
        LOG.info(langid)
        translations = translate(kgids, googleid, key)
        result = []
        for triple in triples:
            if "sub" not in triple or "obj" not in triple or "sub_label" not in triple or "obj_label" not in triple:
                triple["from_english"] = True
                result.append(triple)
            else:
                subid = triple["sub"]
                objid = triple["obj"]
                sub_translated = get_translation(subid, translations, triple)
                obj_translated = get_translation(objid, translations, triple)
                if sub_translated is None or obj_translated is None:
                    triple["from_english"] = True
                    result.append(triple)
                else:
                    triple["from_english"] = False
                    triple["sub_label"] = sub_translated
                    triple["obj_label"] = obj_translated
                    result.append(triple)
        os.makedirs(os.path.join(args.outpath, langid), exist_ok=True)
        with open(os.path.join(args.outpath, langid, args.relation + ".jsonl"), "w") as fout:
            for triple in result:
                fout.write(json.dumps(triple) + "\n")


if __name__ == '__main__':
    main()
