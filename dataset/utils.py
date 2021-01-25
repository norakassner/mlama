import collections
import logging


def rec_dd():
    return collections.defaultdict(rec_dd)


def load_languagemapping(path):
    lang2translateid = {}
    with open(path) as fp:
        next(fp)
        for line in fp:
            if line:
                wikiid, _, _, googleid = line.split("\t")
                if not googleid:
                    # try the other id and see what comes out of google translate
                    googleid = wikiid
                lang2translateid[wikiid.strip()] = googleid.strip()
    return lang2translateid


def get_logger(name, filename=None, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if filename is not None:
        fh = logging.FileHandler(filename)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger