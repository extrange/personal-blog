import datetime
import sys
import time
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def process_dir(folder, target_width=1600, add_dates=False):
    """
    Recursively resize all images in a directory into progressive, quality=80 JPG files with the specified width, preserving aspect ratio
    :param folder: folder to search for image files
    :param target_width: target width
    :param add_dates: whether to read EXIF date information from files and append to output filename
    :return:
    """

    time1 = time.time()

    files = Path(folder)

    # Create output dir if not exists
    output = files.parent / 'output'
    if not output.exists():
        output.mkdir()

    print(f'Output dir is {output}')
    print(f'Target width is {target_width}.')
    print(f'Appending dates.') if add_dates else print(f'NOT appending dates.')
    count = 0

    for file in files.rglob('*'):
        try:
            img = Image.open(file)
        except UnidentifiedImageError:
            print(f'Not an image file: {file}', file=sys.stderr)
            continue
        except Exception as e:
            print(f'Error: {e} for {file}', file=sys.stderr)
            continue

        width, height = img.size
        ratio = height / width
        new_height = round(target_width * ratio)

        filename_component = file.name

        if add_dates:
            exif_data = img.getexif()
            exif_date = exif_data.get(36867)
            if exif_date:
                parsed_date = datetime.datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')
                output_file_path = output / f'{parsed_date.strftime("%Y-%m-%d")}-{file.stem}.jpg'
            else:
                output_file_path = output / f'{file.stem}.jpg'  # todo avoid the repetition
        else:
            output_file_path = output / f'{file.stem}.jpg'

        # Resize and save image
        img.resize((target_width, new_height), Image.LANCZOS).save(output_file_path,
                                                                   format="JPEG",
                                                                   optimize=True,
                                                                   progressive=True,
                                                                   quality=80)
        orig_size = file.stat().st_size
        final_size = output_file_path.stat().st_size
        print(
            f'Saved {filename_component} as {output_file_path.name}, {orig_size / 1_000_000: .2f}MB > {final_size / 1_000_000: .2f}MB')
        count += 1

    print(f'Processed {count} files in {time.time() - time1: .2f}s')
