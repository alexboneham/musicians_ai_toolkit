"""MUSICIAN'S AI TOOLKIT by Alexander Boneham"""

# System imports
import sys
import os
import argparse
import time
from base64 import b64decode
import binascii
import webbrowser
from io import BytesIO

# PyPi imports
from PIL import Image
import openai
from dotenv import load_dotenv


def main(args) -> None:
    """
    Main function for running the command line version of the program.

    The goal is for the Song class to house the actual functionality while
    this function is simply for interfacing with the user at the command line
    and executing the relevant functions.
    """

    # Run arg parser for command line arguments
    pargs = parse_arguments(args)

    # Create Song object
    s = Song(pargs.f, pargs.name)

    s.size = pargs.size
    s.img_format = pargs.format

    # Set up API
    max_attemps = 3
    for i in range(max_attemps):
        # Attempt API config 'max_attemps' times
        print(f"API config loop iteration no. {i+1}")
        try:
            s.configure_api()
            break
        except ValueError:
            pass
        sys.exit("Unable to configure up API")

    while True:
        # Loop command-line program functions depending on user's choices
        try:
            action = prompt_user_action()
        except EOFError:
            print("Goodbye!")
            sys.exit()
        else:
            args = []
            if "args" in action:
                args = action["args"]

            # All functions return the song object.
            res = action["func"](s, *args)  # action["func"] is a callable

            # Print any messages from the function
            if "print" in res:
                print(res["print"])


def parse_arguments(args: list):
    # Run arg parser for command line arguments

    parser = argparse.ArgumentParser(
        description="Use OpenAI's Dall-e image generator",
        epilog="Good luck!",
    )
    parser.add_argument(
        "--size",
        help="The size of your image",
        choices=["sm", "md", "lg"],
        default="sm",
    )
    parser.add_argument(
        "--format",
        help="Format for viewing your image",
        choices=["url", "b64_json"],
        default="url",
    )
    parser.add_argument("-f", help="A text file to read lyrics from", required=True)
    # parser.add_argument(
    #     "-p", help="An optional text prompt to pass to the image generator"
    # )
    parser.add_argument("--name", help="Your song's name", default="My Song")
    return parser.parse_args(args)


def prompt_user_action():
    # Prompt the user for the action they would like to perform

    # Give user usage options
    options = {
        1: {"description": "Get song info", "func": song_info},
        2: {"description": "Rename song", "func": rename_song},
        3: {"description": "Print lyrics", "func": print_lyrics},
        4: {"description": "Add song lyrics", "func": add_song_lyrics},
        5: {"description": "Summarize lyric themes", "func": get_summarize_lyrics},
        6: {
            "description": "Get visual description inspired by lyrics",
            "func": visual_description,
        },
        7: {"description": "Create song art from lyrics", "func": create_song_art},
        8: {
            "description": "Create song art from prompt",
            "func": create_song_art,
            "args": ["user_prompt"],
        },
        9: {"description": "Exit program"},
    }

    hr()
    print("What would you like to do? (enter number...)")
    message = "\n".join(f"{k}: {v['description']}" for k, v in options.items())
    print(message)

    while True:
        try:
            action = int(input().strip())
            if action not in range(1, len(options) + 1):
                raise ValueError
        except ValueError:
            print("Please enter a valid number choice")
            pass
        except EOFError:
            print("Goodbye!")
            sys.exit()
        else:
            # Return action object for execution from main()
            action_obj = options[action]

            if action_obj["description"] == "Exit program":
                # Exit program
                print("Goodbye!")
                sys.exit()

            return action_obj


def song_info(s):
    wait(2)
    # print(s)
    return {"print": s.__str__(), "song": s}


def rename_song(s):
    # Rename the song from the command line interface
    try:
        s.name = input(f"What is {s.name}'s new name? ").strip()
        wait(2)
        # print(f"Song name changed to: {s.name}")
    except ValueError:
        print("Unable to rename song")
        pass
    except EOFError:
        print("Goodbye!")
        sys.exit()
    return {"print": f"Song name changed to: {s.name}", "song": s}


def create_song_art(s, *args):
    prompt = ""
    if "user_prompt" in args:
        # Prompt supplied by user
        try:
            prompt = input("Enter prompt for image generator: ").strip()
        except EOFError:
            print("Goodbye!")
            sys.exit()

    # Call the generate artwork method
    s.generate_song_art(prompt, s.size, s.img_format)
    if s.img_format == "url":
        s.open_art()
    return {"song": s}


def get_summarize_lyrics(s):
    print("You have two options for lyric summary: 'sm' or 'lg'")
    while True:
        try:
            size = input("Which would you like? ").strip()
            if size not in ["sm", "lg"]:
                raise ValueError
            break
        except ValueError:
            print("Not a valid option")
            pass
        except EOFError:
            print("Goodbye!")
            sys.exit()

    s.get_lyric_summary(size=size)
    print(s.lyric_summary["themes"])
    return {"song": s}


def print_lyrics(s):
    wait(2)
    return {"print": s.lyrics, "song": s}


def visual_description(s):
    # Prompt user for themes
    print(
        "Would you like to: 1) provide themes, 2) have them inferred from the lyrics, or 3) go back to menu?"
    )
    while True:
        try:
            usr_prompt = int(input().strip())
            if usr_prompt not in [1, 2, 3]:
                raise ValueError
            break
        except ValueError:
            print("Try again")
            pass
        except EOFError:
            print("Goodbye!")
            sys.exit()

    if usr_prompt == 1:

        print(
            "Great! Write a sentence describing your song's themes. For example: Love, hope, and redemption."
        )
        try:
            themes = input("Themes: ").strip()
        except EOFError:
            print("\nGoodbye!")
            sys.exit()

    elif usr_prompt == 2:
        # Get themes from the song method
        s.get_lyric_summary("sm")
        themes = s.lyric_summary["themes"].lstrip("\n")
        print(f"Themes are: {themes}", end="\n\n")
    elif usr_prompt == 3:
        return
    else:
        raise ValueError

    try:
        description = s.get_visual_description(themes)  # Prints to stdout from method
    except ValueError:
        print("Unable to get description")

    print("Here is your visual description:", description)
    return {"song": s}


def add_song_lyrics(s):
    path = input("Path to new song lyrics text file: ").strip()

    try:
        s.add_lyrics(path)
    except ValueError:
        print("Filename must end in .txt")
    wait(3)
    return {"song": s}


def wait(n: int) -> None:
    for _ in range(n):
        print(".", end=" ", flush=True)
        time.sleep(1)
    print()


def hr():
    print("-" * 10)


"""END OF COMMAND LINE PROGRAM FUNCTIONS"""

"""Song class"""


class Song:
    """
    Song is a class which represents song data: ie lyrics, name, artist, etc,
    and offers methods for manipulation.

    The primary instance method on the Song class is the generate_lyrics() method
    which calls the AI engine to complete a section lyrics using a prompt
    based upon the existing lyrics and song metadata.
    """

    def __init__(self, lyric_file: str, name: str = "My Song") -> None:
        self.name = name
        self.add_lyrics(lyric_file)
        self.size = "sm"
        self.img_format = "url"
        # self.prompt = "An album artwork for a song"

    def __str__(self) -> str:
        return f"Song(name={self.name}, size={self.size}, img_format={self.img_format})"

    """Attributes"""

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if not isinstance(name, str):
            raise ValueError
        self._name = name

    @property
    def lyrics(self) -> str:
        return self._lyrics

    @lyrics.setter
    def lyrics(self, lyrics: str) -> None:
        if not lyrics or not isinstance(lyrics, str):
            raise ValueError

        self._lyrics = lyrics

    @property
    def size(self) -> str:
        return self._size

    @size.setter
    def size(self, size: str) -> None:
        if size not in ["sm", "md", "lg"]:
            raise ValueError
        self._size = size

    @property
    def img_format(self) -> str:
        return self._img_format

    @img_format.setter
    def img_format(self, img_format: str) -> None:
        if img_format not in ["url", "b64_json"]:
            raise ValueError
        self._img_format = img_format

    """Methods"""

    def add_lyrics(self, lyric_file: str) -> None:

        # Opens file and sets lyrics with text contents
        if not lyric_file.endswith(".txt"):
            raise ValueError

        with open(lyric_file, "r") as f:
            self.lyrics = f.read()

    def print_lyrics(self) -> None:
        # print("\n".join(self.lyrics))
        print(self.lyrics)

    def configure_api(self) -> None:
        if ai_models := get_models_list():
            print("Successfully configured API")
            # Print first model from list just for demonstration
            # print(ai_models["data"][0])
        else:
            print("API not able to connect")
            raise ValueError

    def generate_song_art(self, prompt="", size="sm", img_format="url") -> None:
        """Generate an artwork using the Dall-e AI image generator.

        If no prompt is provided one will be created by the AI to describe a visual scene based upon
        the themes of the song lyrics.

        If a prompt is provided this will be used for the image generator. See https://openai.com for tips on
        writing good image prompts.
        """

        if not prompt:
            print("No prompt supplied. Generating prompt based on lyric summary...")
            # Check for summary on Song instance
            try:
                s = self.lyric_summary
                if s["size"] != "sm":
                    raise AttributeError
            except AttributeError:
                # Run the summarize method to get a prompt
                print("Running the summarize method...")
                self.get_lyric_summary(size="sm")

            themes = self.lyric_summary["themes"].lstrip("\n")
            print(f"Themes are: {themes}")

            # Build the prompt for Dall-e
            prompt = self.get_visual_description(themes)
            print(f"Scene is: {prompt}")

        # Call ai helper method to generate song.
        # TODO handle value and runtime errors!!
        if res := generate_img(prompt, size, img_format):
            data = res["data"][0]

            if "url" in data:
                # Save url to class
                self.art_url = data["url"]

            elif "b64_json" in data:
                # Save art to Song object
                try:
                    self._art_bin = b64decode(data["b64_json"])
                except binascii.Error as e:
                    print(e)
                    print("Unable to decode binary image data")
                    raise ValueError
                else:
                    self.save_art()

            else:
                print("Unable to find a url or b64_json object in the returned data")
                raise ValueError

        else:
            print("An error occurred when attempting to generate image")
            raise ValueError

    def open_art(self):
        """Open an artwork URL in the webbrowser.
        This method must be run manually after creating an image with url format.
        """
        if self.art_url:
            webbrowser.open(self.art_url)
        else:
            raise ValueError

    def save_art(self):
        """Save a binary image stream to disk.
        This method is called automatically when generating an image with format set to b64_json
        """
        # TODO add PATH to arguments
        if self._art_bin:
            try:
                with Image.open(BytesIO(self._art_bin)) as img:
                    img.save("song_art.png")
                    print("Song art saved to disk!")
            except OSError:
                print("Error opening image stream")
                raise OSError
        else:
            raise ValueError

    def get_lyric_summary(self, size="sm"):
        # Calls AI helper function and stores the lyrics summary
        if size not in ["sm", "lg"]:
            raise ValueError

        response = summarize_lyrics(self.lyrics, size=size)

        if not response:
            raise ValueError

        themes = response["choices"][0]["text"]

        self.lyric_summary = {
            "size": size,
            "themes": themes,
        }

    def generate_lyric_suggestion(self) -> None:
        # Generates lyric suggestions
        pass

    def get_visual_description(self, themes: str) -> str:
        """Describes, in words, an imaginary visual scene based on a song's themes"""
        if not themes:
            print("Must provide themes")
            raise ValueError

        if description_response := create_visual_descriptor(themes):
            return description_response["choices"][0]["text"]

        raise ValueError


"""AI utility functions"""


def get_models_list() -> list | bool:
    """Hit API for list of AI models.

    This is a free task and doesn't cost tokens.
    Using as a way to test connection to the api.
    Return value is mainly for the purpose of satisfying unit tests.
    """

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY", "DEFAULT KEY")
    try:
        return openai.Model.list()
    except openai.error.OpenAIError:
        return False


def generate_img(p: str, s: str, f: str) -> dict:
    """Create image using OpenAI Dall-e

    POST https://api.openai.com/v1/images/generations
    Sizes must be one of 256x256, 512x512, or 1024x1024.
    """

    sizes = {
        "sm": "256x256",
        "md": "512x512",
        "lg": "1024x1024",
    }

    if not p:
        raise ValueError

    if s not in sizes:
        raise ValueError

    if f not in ["url", "b64_json"]:
        raise ValueError

    try:
        return openai.Image.create(prompt=p, n=1, size=sizes[s], response_format=f)
    except openai.error.OpenAIError as e:
        print(e)
        raise RuntimeError


def summarize_lyrics(lyrics: str, size: str = "sm") -> str:
    """Use Davinci to summarize a set of lyrics

    Takes a string of lyrics and passes it to OpenAI's Davcinci model
    with a set of instructions. The goal is to recieve back a summary of
    the general themes of this song or poem. Optional size parameter.

    Returns the summary string.
    """

    if size not in ["sm", "lg"]:
        raise ValueError

    suffix = " in five words or less"

    # training_prompt = """Summarize the main themes from these song lyrics in five words or less:

    #     Lyrics: Love is in the air\nEverywhere I look around.\nLove is in the air\nEvery sight and every sound.
    #     Themes: Love, omniprescence, and perception.

    #     Lyrics: You say I'm crazy\n'Cause you don't think I know what you've done\nBut when you call me baby\nI know I'm not the only one
    #     Themes: Infidelity, mistrust, and jealousy.

    #     Lyrics: {}
    #     Themes:""".format(
    #     lyrics
    # )

    prompt = "Summarize the themes in this song lyric{suffix}:\n\n{lyrics}".format(
        lyrics=lyrics, suffix=suffix if size == "sm" else ""
    )

    try:
        return openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=64,
            temperature=0.7,
            top_p=1,
            n=1,
        )
    except openai.error.OpenAIError as e:
        print(e)
        raise RuntimeError


def create_visual_descriptor(themes: str) -> dict:
    """Use openAI text completion to create a visual description of a scene,
    inspired by the lyrics of a song"""

    prompt = f"Describe in detail, a visual scene based on the themes of {themes}"

    try:
        return openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=60,
            temperature=0.7,
            top_p=1,
            n=1,
        )
    except openai.error.OpenAIError as e:
        print(e)
        raise RuntimeError


if __name__ == "__main__":
    main(sys.argv[1:])
