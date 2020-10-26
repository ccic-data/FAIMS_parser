FROM ubuntu:focal

RUN apt-get update && apt-get install python3-pip procps -y \
    && rm -rf /var/lib/apt/lists/*

ADD /scripts/FAIMS_parser.py /FAIMS_parser/FAIMS_parser.py


ENV PATH /FAIMS_parser:$PATH
