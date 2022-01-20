# Base
FROM python:3.6

#Install git
RUN  apt-get install -y git

# Clone repo
RUN git clone https://github.com/DaniFdezAlvarez/wikipedia_shexer.git wp


# Base repo file as base dir
WORKDIR wp

# Install project dependencies (if any)
RUN pip install -r requirements.txt


# Execute feature extraction
ENTRYPOINT ["python","-m", "docker.extract_features.script", "/vault/projects/dani-20210701/input.ini"]
C:\Users\Dani\repos-git\wikipedia_shexer\docker\extract_features\Dockerfile