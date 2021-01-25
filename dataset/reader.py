from typing import Text, List, Set, Any, Text, Dict
import os
import json


class MLama(object):
    """docstring for MLama"""

    def __init__(self, path: Text) -> None:
        super(MLama, self).__init__()
        self.path = path
        self.data = {}

    def get_all_languages(self) -> List[Text]:
        # not for all languages templates are available.
        return os.listdir(self.path)

    def get_official_languages(self) -> List[Text]:
        return ["ca", "az", "en", "ar", "uk", "fa", "tr", "it", "el", "ru", "hr", "hi", "sv", "sq", "fr", "ga", "eu", "de", "nl", "et", "he", "es", "bn", "ms", "sr",
                "hy", "ur", "hu", "la", "sl", "cs", "af", "gl", "fi", "ro", "ko", "cy", "th", "be", "id", "pt", "vi", "ka", "ja", "da", "bg", "zh", "pl", "lv", "sk", "lt", "ta", "ceb"]

    def get_relations(self, language) -> List[Text]:
        files = os.listdir(os.path.join(self.path, language))
        return [file.replace(".jsonl", "") for file in files if file != "templates.jsonl"]

    @staticmethod
    def _load_templates(path: Text) -> Dict[Text, Text]:
        templates = {}
        with open(path) as fp:
            for line in fp:
                line = json.loads(line)
                templates[line["relation"]] = line["template"]
        return templates

    @staticmethod
    def _load_triples(path: Text) -> Dict[Text, Dict[Text, Text]]:
        triples = {}
        with open(path) as fp:
            for line in fp:
                line = json.loads(line)
                triples[line["lineid"]] = line
        return triples

    def load(self, languages: List[Text] = [], relations: List[Text] = []) -> None:
        self.data = {}
        if not languages:
            languages = self.get_official_languages()
        for language in languages:
            self.data[language] = {}
            if not relations:
                relations = self.get_relations(language)
            templates = self._load_templates(os.path.join(self.path, language, "templates.jsonl"))
            for relation in relations:
                self.data[language][relation] = {}
                if relation not in templates:
                    print("Template missing for relation {} in language {}.".format(relation, language))
                self.data[language][relation]["template"] = templates.get(relation, "")
                self.data[language][relation]["triples"] = self._load_triples(
                    os.path.join(self.path, language, relation + ".jsonl"))

    @staticmethod
    def is_valid_template(template: Text) -> bool:
        return ("[X]" in template and "[Y]" in template)

    def _fill_templates(self, template: Text, triples: Dict[Text, Dict[Text, Text]], mode: Text) -> Dict[Text, Text]:
        '''
        mode in ["x", "y", "xy"]
        '''
        if not self.is_valid_template(template):
            print("Invalid template: {}".format(template))
            return {}
        else:
            filled_templates = {}
            for triple_id, triple in triples.items():
                filled_templates[triple_id] = template
                if "x" in mode:
                    filled_templates[triple_id] = filled_templates[triple_id].replace("[X]", triple["sub_label"])
                if "y" in mode:
                    filled_templates[triple_id] = filled_templates[triple_id].replace("[Y]", triple["obj_label"])
            return filled_templates

    def fill_all_templates(self, mode: Text):
        for language in self.data:
            for relation in self.data[language]:
                self.data[language][relation]["filled_templates"] = self._fill_templates(
                    self.data[language][relation]["template"], self.data[language][relation]["triples"], mode)


def view_sample():
    import random
    # prints a part of a latex table
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=None, type=str, required=True, help="")
    args = parser.parse_args()
    ml = MLama(args.path)
    ml.load()
    ml.fill_all_templates("xy")
    for lang in ml.data:
        all_instances = []
        for relation in ml.data[lang]:
            all_instances.extend(ml.data[lang][relation]["filled_templates"].values())
        examples = random.sample(all_instances, 3)
        print("\\multirow{{3}}{{0.3cm}}{{{}}}".format(lang), end="")
        for example in examples:
            print(" & {}\\\\".format(example))


if __name__ == '__main__':
    view_sample()
