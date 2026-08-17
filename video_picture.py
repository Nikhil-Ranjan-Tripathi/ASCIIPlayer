import cv2
import os
import time
import shutil

ASCII_CHARS = " .'`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

ASPECT_RATIO = 0.50

def get_terminal_width():
    """Get the current terminal width."""
    return shutil.get_terminal_size().columns


def clear_terminal():
    """Clear screen and move cursor to top-left."""
    print("\033[2J\033[H", end="")


def hide_cursor():
    print("\033[?25l", end="")


def show_cursor():
    print("\033[?25h", end="")


def resize_image(image, new_width):
    height, width = image.shape[:2]

    ratio = height / width

    new_height = max(
        1,
        int(new_width * ratio * ASPECT_RATIO)
    )

    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )


def grayify(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def pixels_to_ascii(image):
    """
    Convert grayscale pixels to ASCII characters.
    """

    result = []

    max_index = len(ASCII_CHARS) - 1

    for pixel in image.flatten():

        index = int(pixel / 255 * max_index)

        result.append(ASCII_CHARS[index])

    return "".join(result)


def frame_to_ascii(image, new_width=120):

    image = resize_image(image, new_width)

    gray_image = grayify(image)

    ascii_str = pixels_to_ascii(gray_image)

    rows = []

    for i in range(0, len(ascii_str), new_width):
        rows.append(ascii_str[i:i + new_width])

    return "\n".join(rows)

def frame_to_color_ascii(image, new_width=120):

    image = resize_image(image, new_width)

    gray = grayify(image)

    result = []

    max_index = len(ASCII_CHARS) - 1

    height, width = gray.shape

    for y in range(height):

        row = []

        for x in range(width):

            brightness = gray[y, x]

            index = int(
                brightness / 255 * max_index
            )

            char = ASCII_CHARS[index]

            b, g, r = image[y, x]

            row.append(
                f"\033[38;2;{r};{g};{b}m{char}"
            )

        row.append("\033[0m")

        result.append("".join(row))

    return "\n".join(result)

def frame_to_halfblock(image, new_width=120):

    """
    Uses ▀ to represent TWO vertical pixels.

    Top pixel    -> foreground color
    Bottom pixel -> background color

    This gives approximately twice the vertical resolution
    compared with normal ASCII.
    """

    image = resize_image(
        image,
        new_width
    )

    height, width = image.shape[:2]

    result = []

    for y in range(0, height - 1, 2):

        row = []

        for x in range(width):

            # Top pixel
            b1, g1, r1 = image[y, x]

            # Bottom pixel
            b2, g2, r2 = image[y + 1, x]

            row.append(
                f"\033[38;2;{r1};{g1};{b1}m"
                f"\033[48;2;{r2};{g2};{b2}m▀"
            )

        row.append("\033[0m")

        result.append("".join(row))

    return "\n".join(result)


def play_ascii_video(
    video_path,
    width=None,
    mode="color"
):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():

        print("Error: Could not open video.")

        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    frame_time = 1 / fps

    if width is None:

        width = get_terminal_width() - 2

    width = max(40, width)

    clear_terminal()
    hide_cursor()

    try:

        while True:

            frame_start = time.perf_counter()

            ret, frame = cap.read()

            if not ret:
                break

            if mode == "ascii":

                output = frame_to_ascii(
                    frame,
                    width
                )

            elif mode == "color":

                output = frame_to_color_ascii(
                    frame,
                    width
                )

            elif mode == "half":

                output = frame_to_halfblock(
                    frame,
                    width
                )

            else:

                print(
                    "Invalid mode. Use: ascii, color or half"
                )

                break

            print("\033[H", end="")

            print(output, end="")

            elapsed = (
                time.perf_counter()
                - frame_start
            )

            sleep_time = frame_time - elapsed

            if sleep_time > 0:

                time.sleep(sleep_time)

    except KeyboardInterrupt:

        pass

    finally:

        cap.release()

        show_cursor()

        print("\033[0m")

play_ascii_video(
    "YOUR VIDEO or PHOTO local address",
    width=120,
    mode="color"
)
