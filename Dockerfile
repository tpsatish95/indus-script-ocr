FROM koallen/anaconda-caffe:gpu

# create an alias for caffe
RUN echo "alias caffe='/root/caffe/build/tools/caffe'" >> ~/.bashrc

# install OpenCV
RUN conda install -y opencv

# change working directory
WORKDIR /root/workspace/

# install python requirements
COPY requirements.txt /root/workspace/requirements.txt
RUN pip install -r requirements.txt

# launch command line
ENTRYPOINT ["/bin/bash"]
