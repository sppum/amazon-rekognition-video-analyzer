# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at
#     http://aws.amazon.com/asl/
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.

import sys
import glob
import cPickle
import datetime
import boto3
import time
import os
import pytz

kinesis_client = boto3.client("kinesis")
last_image = None


# Send frame to Kinesis stream
def encode_and_send_frame(filename, enable_kinesis=True):
    try:
        # retval, buff = cv2.imencode(".jpg", frame)
        with open(filename, 'rb') as fh:
            img_bytes = bytearray(fh.read())

        utc_dt = pytz.utc.localize(datetime.datetime.now())
        now_ts_utc = (utc_dt - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

        frame_package = {
            'ApproximateCaptureTime': now_ts_utc,
            'FrameCount': 0,
            'ImageBytes': img_bytes
        }

        # put encoded image in kinesis stream
        if enable_kinesis:
            print "Sending image to Kinesis"
            response = kinesis_client.put_record(
                StreamName="FrameStream",
                Data=cPickle.dumps(frame_package),
                PartitionKey="partitionkey"
            )
            print response

    except Exception as e:
        print e


def latest_image_in_path(path):
    global last_image
    images = glob.glob(os.path.join(path, '*.jpg'))
    images.sort()
    if images:
        current_last_image = images[-1]
        if last_image == current_last_image:
            return None
        last_image = current_last_image
        return last_image
    return None


def watch_directory(path):
    while True:
        print('checking...')
        image = latest_image_in_path(path)
        if image:
            print('found!')
            encode_and_send_frame(image)
        time.sleep(5)


def main():
    watch_directory(sys.argv[1])


if __name__ == '__main__':
    main()
