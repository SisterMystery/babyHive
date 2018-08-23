FROM tensorflow/magenta

WORKDIR /
ARG log_dir 
RUN mkdir -p $log_dir
RUN mkdir -p /mnt/data
ARG data
COPY $data /
ENV train_data=data/training_poly_tracks.tfrecord
ENV data_tar=$data
