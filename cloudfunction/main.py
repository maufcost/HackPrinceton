# Cloud Function
# Convert Video to Gif
import os
import tempfile
import json

from google.cloud import storage
from moviepy.editor import *
from google.cloud import videointelligence
from GrabzIt import GrabzItAnimationOptions
from GrabzIt import GrabzItClient
from algoliasearch.search_client import SearchClient

client =  ""#SEACHCLIENT
index = client.init_index('vortex')

grabzIt = "" # GRAB
storage_client = storage.Client()
#vision_client = vision.ImageAnnotatorClient()

# Blurs uploaded images that are flagged as Adult or Violence.
def __convert_to_gif(data, context):
    file_data = data
    file_name = file_data["name"]
    bucket_name = file_data["bucket"]
    blob = storage_client.bucket(bucket_name).get_blob(file_name)
    blob_uri = f"gs://{bucket_name}/{file_name}"
    return __convert_video(blob)


def __convert_video(current_blob):
    file_name = current_blob.name
    _, temp_local_filename = tempfile.mkstemp()

    # Download file from bucket.
    current_blob.download_to_filename(temp_local_filename)
    print(f"Image {file_name} was downloaded to {temp_local_filename}.")


    options = GrabzItAnimationOptions.GrabzItAnimationOptions()
    options.framesPerSecond = 10
    options.duration = 3
    options.start = 0
    options.width = 640
    options.height = 360

    grabzIt.URLToAnimation("https://storage.googleapis.com/vortexvideo/{}".format(file_name), options)
    grabzIt.SaveTo(temp_local_filename)

    print(f"Video {file_name} was Converted.")

    # Upload result to a second bucket, to avoid re-triggering the function.
    # You could instead re-upload it to the same bucket + tell your function
    # to ignore files marked as blurred (e.g. those with a "blurred" prefix)
    blur_bucket_name = "vortexgif"
    blur_bucket = storage_client.bucket(blur_bucket_name)
    new_blob = blur_bucket.blob(file_name+".gif")
    new_blob.upload_from_filename(temp_local_filename)
    print(f"Blurred image uploaded to: gs://{blur_bucket_name}/{file_name}")

def video_annotate(data, context):
    file_data = data
    file_name = file_data["name"]
    bucket_name = file_data["bucket"]

    blob = storage_client.bucket(bucket_name).get_blob(file_name)
    blob_uri = f"gs://{bucket_name}/{file_name}"

    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.Feature.LABEL_DETECTION]

    mode = videointelligence.LabelDetectionMode.SHOT_AND_FRAME_MODE
    config = videointelligence.LabelDetectionConfig(label_detection_mode=mode)
    context = videointelligence.VideoContext(label_detection_config=config)

    operation = video_client.annotate_video(
        request={"features": features, "input_uri": blob_uri, "video_context": context}
    )
    print("\nProcessing video for label annotations:")

    result = operation.result(timeout=180)
    print("\nFinished processing.")

    all_labales = []
    collected_labels = {}
    #Process frame level label annotations
    frame_labels = result.annotation_results[0].frame_label_annotations
    for i, frame_label in enumerate(frame_labels):

        print("Frame label description: {}".format(frame_label.entity.description))
        for category_entity in frame_label.category_entities:
            print(
                "\tLabel category description: {}".format(category_entity.description)
            )

        # Each frame_label_annotation has many frames,
        # here we print information only about the first frame.
        frame = frame_label.frames[0]
        time_offset = frame.time_offset.seconds + frame.time_offset.microseconds / 1e6
        collected_labels[frame_label.entity.description] = {'offset':time_offset, 'confidence':frame.confidence}
        all_labales.append(frame_label.entity.description)
        print("\tFirst frame time offset: {}s".format(time_offset))
        print("\tFirst frame confidence: {}".format(frame.confidence))
        print("\n")

    final_dict = {'vidID':file_name, 'labels':all_labales, 'data':collected_labels}
    index.save_object(final_dict, {'autoGenerateObjectIDIfNotExist': True})
    index.set_settings({"searchableAttributes": ["labels","vidID"]})
    print("######################@@@@@@@@@@@@@@@@@@@@@@@@@")
    __convert_to_gif(data, context)
