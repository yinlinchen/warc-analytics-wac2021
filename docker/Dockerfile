FROM continuumio/anaconda:2019.07
LABEL maintainer="ylchen@vt.edu"

ENV PATH="${PATH}:/opt/conda/bin"

# Install Jupyter and Java
RUN /opt/conda/bin/conda install openjdk=8.0.152 jupyter -y --quiet

# Install AWS Cli
RUN apt-get update && apt-get install -y awscli

# Create folders
RUN mkdir -p /config
RUN mkdir -p /notebooks
RUN mkdir -p /data
RUN mkdir -p /results

# Copy files
COPY jupyter_notebook_config.py /jupyter_notebook_config.py
COPY extractwarc.ipynb /extractwarc.ipynb

COPY setup.sh /notebooks/setup.sh
RUN chmod +x /notebooks/setup.sh

COPY kernel.json /kernel.json

COPY executeNotebook.sh /executeNotebook.sh
RUN chmod +x /executeNotebook.sh

# Setup and run
VOLUME /config
VOLUME /notebooks

WORKDIR /notebooks
CMD ["/notebooks/setup.sh"]
