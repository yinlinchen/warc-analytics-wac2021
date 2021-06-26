#!/bin/sh
echo "Running..."

echo ${WARC_FILENAME}

cd /data
wget https://commoncrawl.s3.amazonaws.com/crawl-data/CC-MAIN-2020-24/segments/${WARC_URL}${WARC_FILENAME}.warc.gz
cd /notebooks

jupyter nbconvert --to notebook --execute extractwarc.ipynb --output=${WARC_FILENAME}_output.ipynb --ExecutePreprocessor.timeout=-1

mkdir -p /results/${WARC_FILENAME}
mv ${WARC_FILENAME}_output.ipynb /results/${WARC_FILENAME}/

# Upload results to specific folder
aws s3 sync /results/${WARC_FILENAME}/ s3://warcresults/${WARC_FILENAME}/

echo "Done."