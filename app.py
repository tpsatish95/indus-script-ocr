import sys

from stages import extract_seal


if __name__ == '__main__':
    input_artifact_image_path = sys.argv[1]

    seal = extract_seal.crop_white(input_artifact_image_path)
