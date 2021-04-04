# Cloud Function
# Convert Video to Gif
import os
import tempfile

from google.cloud import storage
from moviepy.editor import *
from google.cloud import videointelligence

storage_client = storage.Client()
#vision_client = vision.ImageAnnotatorClient()

# Convert video uploaded to vortex to a gif
def __convert_to_gif(data, context):
    file_data = data
    file_name = file_data["name"]
    bucket_name = file_data["bucket"]

    blob = storage_client.bucket(bucket_name).get_blob(file_name)
    blob_uri = f"gs://{bucket_name}/{file_name}"
    #blob_source = vision.Image(source=vision.ImageSource(gcs_image_uri=blob_uri))

    # # Ignore already-blurred files
    # if file_name.startswith("blurred-"):
    #     print(f"The image {file_name} is already blurred.")
    #     return

    # Process image
    __convert_video(blob)

def __convert_video(current_blob):
    file_name = current_blob.name
    _, temp_local_filename = tempfile.mkstemp()

    # Download file from bucket.
    current_blob.download_to_filename(temp_local_filename)
    print(f"Image {file_name} was downloaded to {temp_local_filename}.")

    clip = VideoFileClip(temp_local_filename)
    clip = clip.subclip(0, 3)
    clip.write_gif(temp_local_filename + ".gif")

    # Upload result to a second bucket, to avoid re-triggering the function.
    # You could instead re-upload it to the same bucket + tell your function
    # to ignore files marked as blurred (e.g. those with a "blurred" prefix)
    gif_bucket_name = os.getenv("vortexgif")
    gif_bucket = storage_client.bucket(blur_bucket_name)
    new_blob = gif_bucket.blob(file_name)
    new_blob.upload_from_filename(temp_local_filename+".gif")
    print(f"Blurred image uploaded to: gs://{blur_bucket_name}/{file_name}")
    os.remove(temp_local_filename+".gif")

def video_annotate(data, context):
    file_data = data
    file_name = file_data["name"]
    bucket_name = file_data["bucket"]

    blob = storage_client.bucket(bucket_name).get_blob(file_name)
    blob_uri = f"gs://{bucket_name}/{file_name}"
    #blob_source = vision.Image(source=vision.ImageSource(gcs_image_uri=blob_uri))

    """ Detects labels given a GCS path. """
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

    # Process video/segment level label annotations
    segment_labels = result.annotation_results[0].segment_label_annotations
    for i, segment_label in enumerate(segment_labels):
        print("Video label description: {}".format(segment_label.entity.description))
        for category_entity in segment_label.category_entities:
            print(
                "\tLabel category description: {}".format(category_entity.description)
            )

        for i, segment in enumerate(segment_label.segments):
            start_time = (
                segment.segment.start_time_offset.seconds
                + segment.segment.start_time_offset.microseconds / 1e6
            )
            end_time = (
                segment.segment.end_time_offset.seconds
                + segment.segment.end_time_offset.microseconds / 1e6
            )
            positions = "{}s to {}s".format(start_time, end_time)
            confidence = segment.confidence
            print("\tSegment {}: {}".format(i, positions))
            print("\tConfidence: {}".format(confidence))
        print("\n")

    # Process shot level label annotations
    shot_labels = result.annotation_results[0].shot_label_annotations
    for i, shot_label in enumerate(shot_labels):
        print("Shot label description: {}".format(shot_label.entity.description))
        for category_entity in shot_label.category_entities:
            print(
                "\tLabel category description: {}".format(category_entity.description)
            )

        for i, shot in enumerate(shot_label.segments):
            start_time = (
                shot.segment.start_time_offset.seconds
                + shot.segment.start_time_offset.microseconds / 1e6
            )
            end_time = (
                shot.segment.end_time_offset.seconds
                + shot.segment.end_time_offset.microseconds / 1e6
            )
            positions = "{}s to {}s".format(start_time, end_time)
            confidence = shot.confidence
            print("\tSegment {}: {}".format(i, positions))
            print("\tConfidence: {}".format(confidence))
        print("\n")

    # Process frame level label annotations
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
        print("\tFirst frame time offset: {}s".format(time_offset))
        print("\tFirst frame confidence: {}".format(frame.confidence))
        print("\n")
    __convert_to_gif(data, context)
