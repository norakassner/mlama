WORKDIR="/mounts/work/philipp/tmp/mlama"

# 1. Download TREx and GoogleRE
wget https://dl.fbaipublicfiles.com/LAMA/data.zip -P ${WORKDIR}
unzip ${WORKDIR}/data.zip -d ${WORKDIR} && rm ${WORKDIR}/data.zip

# 2. Translate TREx

# download entity data
mkdir -p ${WORKDIR}/data/wikidata_entities

python download_trexentities.py \
--datapath ${WORKDIR}/data/TREx \
--outpath ${WORKDIR}/data/wikidata_entities

# create multilingual json files
mkdir -p ${WORKDIR}/data/multilingual
python translate_trex.py \
--data ${WORKDIR}/data/TREx \
--entities ${WORKDIR}/data/wikidata_entities \
--outpath ${WORKDIR}/data/multilingual \
--languagemapping mbertlangs.txt


# 3. Translate GoogleRE
# You will need a valid Google Knowledge Graph API key in the environment variable `GOOGLEAPIKEY for this section
mv ${WORKDIR}/data/Google_RE/date_of_birth_test.jsonl ${WORKDIR}/data/Google_RE/date_of_birth.jsonl
mv ${WORKDIR}/data/Google_RE/place_of_birth_test.jsonl ${WORKDIR}/data/Google_RE/place_of_birth.jsonl
mv ${WORKDIR}/data/Google_RE/place_of_death_test.jsonl ${WORKDIR}/data/Google_RE/place_of_death.jsonl

for relation in date_of_birth place_of_death
do
	python translate_googlere.py \
	--inputpath ${WORKDIR}/data/Google_RE \
	--relation ${relation} \
	--outpath ${WORKDIR}/data/multilingual \
	--languagemapping mbertlangs.txt
done

# 4.1. Translate Templates TREx
mkdir -p ${WORKDIR}/data/multilingual/templates_original
python translate_templates.py translate \
	--templates ${WORKDIR}/data/relations.jsonl \
	--outfile ${WORKDIR}/data/multilingual/templates_original \
	--languagemapping mbertlangs.txt


# 4.2. Translate Templates GoogleRE
# manually copy the two googlere relations templates and translate them
python translate_templates.py translate \
	--templates ${WORKDIR}/data/relations_googlere.jsonl \
	--outfile ${WORKDIR}/data/multilingual/templates_original \
	--languagemapping mbertlangs.txt

# 4.3. Clean Templates in place
cp -r ${WORKDIR}/data/multilingual/templates_original ${WORKDIR}/data/multilingual/templates
python translate_templates.py clean \
	--templates ${WORKDIR}/data/multilingual/templates

# 5. Copy each template json into the language folder
mkdir -p ${WORKDIR}/data_clean
python cleanup.py \
    --infolder ${WORKDIR}/data/multilingual \
    --outfolder ${WORKDIR}/data_clean

# 6. Load mLAMA
python reader.py --path ${WORKDIR}/data_clean/




