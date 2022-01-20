# Base
FROM python:3.9

#Install git
RUN  apt-get install -y git

# Clone repo
RUN git clone https://github.com/DaniFdezAlvarez/wikipedia_shexer.git wps


# Base repo file as base dir
WORKDIR wps

# Install project dependencies (if any)
RUN pip install -r requirements.txt


# Execute feature extraction
ENTRYPOINT ["python","-m", "playground.generate_sliced_shapes", ">", "/ws_app/output_r_candidates.txt"]
