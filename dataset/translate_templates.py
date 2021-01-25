from googletrans import Translator
import json
import os
import argparse
from utils import get_logger

LOG = get_logger(__name__)


def fix_template(template, lang):
    # general rules
    if "[X]" not in template:
        template = template.replace("X", "[X]", 1)
    if "[Y]" not in template:
        template = template.replace("Y", "[Y]", 1)
        template = template.replace("[Y ]", "[Y] ", 1)

    if lang == "tl":
        template = template.replace("Naglalaro ang [X] sa posisyon.", "Naglalaro si [X] sa posisyon na [Y]", 1)
        template = template.replace("Sumali sa [X] ang [X].", "Sumali ang [X] sa [Y].", 1)
        template = template.replace("Naglalaro ang [X] ng musika.", "Naglalaro si [X] ng [Y] musika.", 1)
        template = template.replace("Naglalaro ang [X].", "Ginawa ni [X] ang [Y].", 1)
    if lang == "el":
        template = template.replace("[Χ]", "[X]", 1)
        template = template.replace("[Υ]", "[Y]", 1)
        if "[Y]" in template and "[X]" not in template:
            template = template.replace("[Ο]", "[X]", 1)
        if "[X]" in template and "[Y]" not in template:
            template = template.replace("[Ο]", "[Y]", 1)
    if lang == "ceb":
        # to be checked
        template = template.replace("Natawo sa [Y].", "Natawo ang [X] sa [Y].", 1)
        template = template.replace("Nag-apil sa [X] ang [X].", "Ang [X] miapil sa [Y].", 1)

    if lang == "pa":
        template = template.replace("[ਐਕਸ]", "[X]", 1)
        template = template.replace("[ਵਾਈ]", "[Y]", 1)
    if lang == "ta":
        template = template.replace("[எக்ஸ்]", "[X]", 1)
        template = template.replace("[ஒய்]", "[Y]", 1)
    if lang == "mg":
        template = template.replace(
            "Tamin'ny voalohany, nalefan'i [Y] tany am-boalohany.", "Tamin'ny voalohany, ny X [X] dia nalefa tamin'ny [Y].", 1)
    if lang == "gu":
        template = template.replace("[એક્સ]", "[X]", 1)
        template = template.replace("[વાય]", "[Y]", 1)
    if lang == "mr":
        template = template.replace("[एक्स]", "[X]", 1)
        template = template.replace("[वाई]", "[Y]", 1)
        template = template.replace("[वाय]", "[Y]", 1)
    if lang == "sr":
        template = template.replace("[Кс]", "[X]", 1)
        template = template.replace("[И]", "[Y]", 1)
        template = template.replace("[X] је рођен у И.", "[X] је рођен у [Y].", 1)
    if lang == "kk":
        template = template.replace("[Х] университетте білім алған.", "[X] [Y] университетінде білім алған.", 1)
        template = template.replace("Ана тілі [Х] болып табылады.", "[Х] -дің ана тілі - [Y].", 1)
        template = template.replace("[Х]", "[X]", 1)
        template = template.replace("[Y]", "[Y]", 1)
    if lang == "kn":
        template = template.replace("[ಎಕ್ಸ್]", "[X]", 1)
        template = template.replace("[ವೈ]", "[Y]", 1)
    if lang == "ne":
        template = template.replace("[एक्स]", "[X]", 1)
        template = template.replace("[Y]", "[Y]", 1)
    if lang == "hy":
        template = template.replace("[X]", "[X]", 1)
        template = template.replace("[Յ]", "[Y]", 1)
    if lang == "uz":
        template = template.replace("[X] universitetida tahsil olgan.", "[X] [Y] universitetida tahsil olgan.", 1)
        template = template.replace("[X] din bilan bog'liq.", "[X] [Y] diniga mansub.", 1)
    if lang == "tg":
        template = template.replace("[X] аз рӯи касб аст.", "[X] аз рӯи касб [Y] аст.", 1)
        template = template.replace("[Ю]", "[Y]", 1)
        template = template.replace("[Х]", "[X]", 1)
        template = template.replace("[Y]", "[Y]", 1)
    if lang == "lt":
        template = template.replace(
            "Buvo įgijęs išsilavinimą [Y] universitete.", "[X] įgijo išsilavinimą [Y] universitete.", 1)
    if lang == "bn":
        template = template.replace("[এক্স]", "[X]", 1)
        template = template.replace("[ওয়াই]", "[Y]", 1)
    if lang == "la":
        template = template.replace("[K]", "[Y]", 1)
        template = template.replace("[A]", "[Y]", 1)
        template = template.replace("[N]", "[Y]", 1)
        template = template.replace("[V]", "[Y]", 1)
        template = template.replace("[ego]", "[Y]", 1)
        template = template.replace("[Ego]", "[Y]", 1)
    if lang == "hi":
        if "[X]" not in template:
            template = template.replace("[एक्स]", "[X]", 1)
        if "[Y]" not in template:
            template = template.replace("[वाई]", "[Y]", 1)
    return template


def clean(args):
    to_fix = []
    broken = 0
    for file in os.listdir(args.templates):
        with open(os.path.join(args.templates, file), "r") as fp:
            for line in fp:
                if line:
                    template = json.loads(line)
                    #lang = file.replace(".jsonl", "").split("_")[-1]
                    #template["template"] = fix_template(template["template"], lang)
                    if template["template"].count("[X]") != 1 or template["template"].count("[Y]") != 1:
                        LOG.warning("Broken Template {} {} {}".format(file, template["relation"], template["template"]))
                        to_fix.append(file)
                        broken += 1
    to_fix = set(to_fix)
    LOG.info("Fixing {} broken templates across {} languages.".format(broken, len(to_fix)))
    for file in to_fix:
        with open(os.path.join(args.templates, file), "r") as fp:
            fixed_templates = []
            for line in fp:
                if line:
                    template = json.loads(line)
                    lang = file.replace(".jsonl", "").split("_")[-1]
                    if template["template"].count("[X]") != 1 or template["template"].count("[Y]") != 1:
                        template["template"] = fix_template(template["template"], lang)
                    fixed_templates.append(template)
        with open(os.path.join(args.templates, file), "w") as fp:
            for line in fixed_templates:
                fp.write(json.dumps(line) + "\n")


def translate(args):
    lang2translateid = {}
    with open(args.languagemapping) as fp:
        next(fp)
        for line in fp:
            if line:
                wikiid, _, _, googleid = line.split("\t")
                if not googleid:
                    # try the other id and see what comes out of goole translate
                    googleid = wikiid
                lang2translateid[wikiid.strip()] = googleid.strip()

    templates = []
    with open(args.templates) as fp:
        for line in fp:
            if line:
                templates.append(json.loads(line))

    # get translations
    for wikiid, googleid in lang2translateid.items():
        LOG.info("TRANSLATING {}".format(wikiid))
        translated = []
        for template in templates:
            try:
                translator = Translator()
                result = translator.translate(template["template"], src="en", dest=googleid)
                translated_template = template.copy()
                translated_template["template"] = result.text
                translated.append(translated_template)
            except Exception as e:
                LOG.info("Exception: {}".format(e))
        if len(translated) != len(templates):
            LOG.warning("Not all translations succesful!")
            LOG.warning("Skipping language")
        else:
            # write out
            with open(os.path.join(args.outfile, "relations_{}.jsonl".format(wikiid)), "w") as fout:
                for template in translated:
                    fout.write("{}\n".format(json.dumps(template)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_translate = subparsers.add_parser('translate')
    parser_translate.set_defaults(func=translate)
    parser_translate.add_argument("--templates", default=None, type=str, required=True, help="")
    parser_translate.add_argument("--languagemapping", default=None, type=str, required=True, help="")
    parser_translate.add_argument("--outfile", default=None, type=str, required=True, help="")

    parser_clean = subparsers.add_parser('clean')
    parser_clean.set_defaults(func=clean)
    parser_clean.add_argument("--templates", default=None, type=str, required=True, help="")

    args = parser.parse_args()
    args.func(args)
