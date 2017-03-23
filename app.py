import sys

from stages import bg_crop


if __name__ == '__main__':
    input_artifact_image_path = sys.argv[1]

    bg_crop.crop_white(input_artifact_image_path)
