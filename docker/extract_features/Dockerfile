FROM python 3.6  # base

#Install git
RUN  apt-get install -y git

# Clone repo
RUN git clone https://github.com/DaniFdezAlvarez/wikipedia_shexer.git wds

# Base repo file as base dir
WORKDIR wds

# Install project dependencies
RUN pip install requirements.txt

# Get the input from the actual machine
COPY ./params.ini .

# Execute feature extraction
CMD python -m playground/docker_extract_features params.ini

# Get the results out of the container??