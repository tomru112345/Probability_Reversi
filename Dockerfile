FROM tensorflow/tensorflow:2.8.4-gpu
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y
RUN apt-get autoremove -y
RUN apt-get autoclean -y

RUN apt-get install -y gnupg2 curl
RUN apt-get install -y software-properties-common tzdata
RUN apt-get install -y git
ENV TZ=Asia/Tokyo
RUN add-apt-repository ppa:deadsnakes/ppa

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update -y
RUN apt-get install python3-dev -y
RUN apt-get install g++ -y
RUN apt-get install vim -y
RUN apt-get -y install python3-distutils

RUN python3 -m pip install -U pip wheel setuptools
RUN python3 -m pip install protobuf==3.20
RUN python3 -m pip install pybind11

RUN mkdir /git
RUN git clone https://github.com/tomru112345/Probability_Reversi.git /git
