# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at
#     http://aws.amazon.com/asl/
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.

from __future__ import print_function
import base64
import datetime
import time
import decimal
import uuid
import json
import cPickle
import boto3
import pytz
from pytz import timezone


def load_config():
    '''Load configuration from file.'''
    with open('imageprocessor-params.json', 'r') as conf_file:
        conf_json = conf_file.read()
        return json.loads(conf_json)


def convert_ts(ts, config):
    '''Converts a timestamp to the configured timezone. Returns a localized datetime object.'''
    tz = timezone(config['timezone'])
    utc = pytz.utc

    utc_dt = utc.localize(datetime.datetime.utcfromtimestamp(ts))

    localized_dt = utc_dt.astimezone(tz)

    return localized_dt


def process_image(event, context):

    # Initialize clients
    rekog_client = boto3.client('rekognition')
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')

    # Load config
    config = load_config()

    s3_bucket = config["s3_bucket"]
    s3_key_frames_root = config["s3_key_frames_root"]

    ddb_table = dynamodb.Table(config["ddb_table"])
    ddb_info_table = dynamodb.Table(config["users_table"])

    collection_id = config.get("ImagesCollection")

    stored_count = 0

    # Iterate on frames fetched from Kinesis
    for record in event['Records']:

        frame_package_b64 = record['kinesis']['data']
        frame_package = cPickle.loads(base64.b64decode(frame_package_b64))

        img_bytes = frame_package["ImageBytes"]
        approx_capture_ts = frame_package["ApproximateCaptureTime"]

        now_ts = time.time()

        frame_id = str(uuid.uuid4())
        processed_timestamp = decimal.Decimal(now_ts)
        approx_capture_timestamp = decimal.Decimal(approx_capture_ts)

        now = convert_ts(now_ts, config)
        year = now.strftime("%Y")
        mon = now.strftime("%m")
        day = now.strftime("%d")
        hour = now.strftime("%H")

        try:
            response = rekog_client.search_faces_by_image(
                Image={
                    'Bytes': img_bytes
                },
                CollectionId=collection_id
            )
        except:
            # SDK throws an exception if there are no faces in image
            continue

        # Iterate on rekognition labels. Enrich and prep them for storage in
        # DynamoDB
        faces = []
        for face_match in response['FaceMatches']:
            print(face_match)
            face_id = face_match['Face']['FaceId']
            image_id = face_match['Face']['ImageId']
            external_id = face_match['Face']['ExternalImageId']
            confidence = decimal.Decimal(face_match['Face']['Confidence'])
            try:
                image_info = ddb_info_table.get_item(Key={'image_file': external_id})
                person_name = image_info['Item']['name']
            except KeyError:
                person_name = None
            faces.append({
                'face_id': face_id,
                'image_id': image_id,
                'external_id': external_id,
                'confidence': confidence,
                'person_name': person_name
            })

        if faces:
            # Store frame image in S3
            s3_key = (s3_key_frames_root + '{}/{}/{}/{}/{}.jpg').format(year, mon, day, hour, frame_id)

            s3_client.put_object(
                Bucket=s3_bucket,
                Key=s3_key,
                Body=img_bytes
            )

            # Persist frame data in dynamodb
            item = {
                'frame_id': frame_id,
                'processed_timestamp': processed_timestamp,
                'approx_capture_timestamp': approx_capture_timestamp,
                'processed_year_month': year + mon,  # To be used as a Hash Key for DynamoDB GSI
                's3_bucket': s3_bucket,
                's3_key': s3_key,
                'faces': faces
            }

            ddb_table.put_item(Item=item)

            stored_count += 1

    print('Successfully processed {} records (stored {}).'.format(len(event['Records']), stored_count))
    return


def handler(event, context):
    return process_image(event, context)
