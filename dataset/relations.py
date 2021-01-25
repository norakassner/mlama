import os
from typing import Text, List, Set
import collections
import tqdm
import json


class Relations(object):
    """docstring for Relations"""

    def __init__(self, path: Text, suffix: Text = ".jsonl") -> None:
        self.path = path
        self.suffix = suffix
        self.data = collections.defaultdict(list)

    def get_available_filenames(self) -> List[Text]:
        filenames = []
        for file in os.listdir(self.path):
            filenames.append(file.replace(self.suffix, ""))
        return filenames

    def load_data(self, filenames: List[Text]) -> None:
        for filename in tqdm.tqdm(filenames):
            with open(os.path.join(self.path, filename + self.suffix)) as fp:
                for line in fp:
                    if line:
                        self.data[filename].append(json.loads(line))

    def get_all_entities(self, fields: List[Text]) -> Set[Text]:
        entities = set()
        for filename, triples in self.data.items():
            for triple in triples:
                for field in fields:
                    if field in triple:
                        entities.add(triple[field].strip())
        return entities

