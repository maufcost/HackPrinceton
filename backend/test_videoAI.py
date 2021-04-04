#Import libraries
#import argparse
#Load the full path of JSON file obtained in step 1. Replace '/Users/harry/Downloads/SampleProject-1abc.json' with your filepath
import os
from google.cloud import videointelligence
from algoliasearch.search_client import SearchClient

# client = SearchClient.create('redacted', 'redacted')
# index = client.init_index('vortex')

""" Detects labels given a GCS path. """
video_client = videointelligence.VideoIntelligenceServiceClient()
features = [videointelligence.Feature.LABEL_DETECTION]

mode = videointelligence.LabelDetectionMode.SHOT_AND_FRAME_MODE
config = videointelligence.LabelDetectionConfig(label_detection_mode=mode)
context = videointelligence.VideoContext(label_detection_config=config)

operation = video_client.annotate_video(
    request={"features": features, "input_uri": "gs://vortexvideo/video.mp4", "video_context": context}
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

final_dict = {'labels':all_labales, 'data':collected_labels}
index.save_object(final_dict, {'autoGenerateObjectIDIfNotExist': True})
index.set_settings({"searchableAttributes": ["labels"]})
print("######################@@@@@@@@@@@@@@@@@@@@@@@@@")
