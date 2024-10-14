import sys
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, vfx

def video_editor(video_files: list[str], output_filename: str):
    """
    This function takes a list of video files, resizes and crops them to fit YouTube Shorts dimensions, and concatenates them into a single video file.

    :param video_files: A list of paths to video files.
    :param output_filename: The path to the output video file.
    :return: The path to the output video file.
    """

    clips = []
    for video in video_files:
        try:
            # Load the video file
            clip = VideoFileClip(video)

            # Set target dimensions for YouTube Shorts
            target_width = 1080
            target_height = 1920

            # Determine the scaling factor to cover the target dimensions
            clip_width, clip_height = clip.size
            width_ratio = target_width / clip_width
            height_ratio = target_height / clip_height
            scaling_factor = max(width_ratio, height_ratio)

            # Resize the clip to cover the target area
            clip_resized = clip.resize(height=int(clip.h * scaling_factor))

            # Center crop the clip to target dimensions
            clip_cropped = clip_resized.crop(
                x_center=clip_resized.w / 2,
                y_center=clip_resized.h / 2,
                width=target_width,
                height=target_height
            )

            # Optionally limit the clip duration to 60 seconds
            # clip_cropped = clip_cropped.subclip(0, min(clip_cropped.duration, 60))

            clips.append(clip_cropped)
        except Exception as e:
            print(f"Error processing {video}: {e}")
            continue

    if not clips:
        print("No valid video clips were processed.")
        sys.exit(1)

    # Concatenate clips
    final_clip = concatenate_videoclips(clips, method='compose')

    # Write the final video file
    final_clip.write_videofile(
        output_filename,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        threads=4
    )

    return output_filename