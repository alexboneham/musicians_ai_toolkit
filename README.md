# MUSICIAN'S AI TOOLKIT
### Alexander Boneham

#### Video Demo: https://youtu.be/30OGvLXJj4I

#### Description:

A Python-based toolkit designed for musicians, composers, singers and songwriters, to aid in the creative pursuits of music composition and production. The main feature of this toolkit is the ability to harness OpenAI's artificial intelligence engines to work with song lyrics and album artwork. The program can be imported as a **package/module** with all features available to the programmer, or run as a **command-line program**, calling upon the the same Song class' functionality from the command-line.

The core of the program revolves around an instance of the Song class. The class contains various attributes and methods for working with lyrics and artwork such as creating summaries of themes and dynamically generating album artwork. In general any logic that deals with the OpenAI API has been separated out and exists in separate functions which are then called by the Song class' methods.

Similarly much of the logic dealing with the command-line functionality has been separated out into various utility functions. This is mostly to facilitate specific and accurate unit testing as well as for general organization. The command-line program runs from the `main()` function of `project.py`.

---

#### A Note on Image Generation

The Song class contains a method for generating album artworks called _generate_song_art()_. This method can function in two general ways:

1. Calling it without arguments. This is the intended usage, at least for this project. The program will use two different AI engines to generate an image. First it asks the GPT davinci model to read a song's lyrics and describe in detail a visual scene, based on the lyric's themes. It will then pass this visual descriptor into the Dall-e image generation engine to create an image,
2. By passing the the method a prompt to describe the image you want generated. In this way the method really just acts as an interface with the API and has nothing to do with the song's lyrics or themes. You could tell it to "draw an image of a cat in a top hat" and the AI would go to work generating the image (maybe your song is about fancy cats?). Read the [image generation guide](https://beta.openai.com/docs/guides/images) at [openai.com](https://openai.com) for tips on engineering good prompts for the Dall-e model.

---

#### Usage

To run the command-line program, download or clone the project repository.

In your root directory, create a virtual environment:

```Python
python3 -m venv env
```

And activate it:

```Python
source env/bin/activate
```

Install the required packages with pip:

```Python
pip install -r requirements.txt
```

You will need to sign up at [OpenAI](https://openai.com) and generate your own API key to use the program.

In your root directory, create a `.env` file:

```
touch .env
```

Save the key in the `.env` file as:

```Python
OPENAI_API_KEY=MY_SECRET_KEY
```

replacing "MY_SECRET_KEY" with your key from OpenAI. The program will take care of finding your dotenv file and getting the key's value.

Run the command-line program with the -f flag as a `.txt` file. This is **required** to initialize the Song instance with a song's lyrics.

```
python3 project.py -f hello.txt
```

Run the command-line program's help to explore usage options:

```
python3 project.py --help
```

There are three optional flags that can be applied when running the command-line program, both relate to the image generation feature.

- --size : The size of your image. Choices are ["sm", "md", "lg"]. Defaults to "sm".
- --format : The format for viewing the image. Choices are ["url", "b64_json"]. Defaults to "url".
- --name: A name for your song. Defaults to "My Song".

The "url" flag means that the generated artwork will be saved to a temporary url and opened in the default browser.

The "b64_json" flag is used to save the file to disk. If the flag is used, the image generator will return a byte-stream that will then be decoded and saved to disk as "song_art.png".

---

# Song

Class containing all song info and methods

## Overview

The Song class is an object for storing, generating and manipulating song data.

_class_ **Song**(_lyric_file_, [_name='My Song'_])

Create an object with lyrics read from a supplied text file. Optional argument name defaults to "My Song".

### Song attributes

- **Song**.name - Used to set or return the name of the Song instance. Defaults to "My Song". Must be a string.

- **Song**.lyrics - A song's lyrics stored as a string. This should be set via a call to the add_lyrics() method, not directly.

- **Song**.size - Used to set or get intended image size. Options: ["sm", "md", "lg"] defaults to "sm".

- **Song**.img_format - Used to set or get intended image format. Options ["url", "b64_json"] defaults to "url", meaning a url is generated to view your image. Choose b64_json to save the image to disk.

- ~~**Song**.prompt - Used to set or get the prompt for generating song art. Defaults to "An album artwork for a song". Must be a string.~~

- **Song**.lyric_summary - AI generated summary of lyric themes. This is set after calling _get_lyric_summary()_

### Song methods

Songs come with a number of methods for working with lyrics, metadata and the like.

- Song.**add_lyrics**(_lyrics_file_: str)

Set the lyrics for the Song from a text file. File **must** end in '.txt'. ~~The method reads lines from the text file, creating a list with each element representing one line of lyrics~~ -> Now the method simply reads from the text file and sets the lyrics as a string.

- Song.**print_lyrics**()

Prints a song's lyrics to sys.stdout ~~with each line separated by a line break~~.

- Song.**configure_api**()

Calls AI helper function to set api_key and test connection. If connection is successful prints to stdout, else prints message and raises ValueError. Note this must be called **before** attempting any other calls to AI functions such as generate_song_art.

- Song.**generate_song_art**(_[prompt="", size="sm", img_format="url"]_)

Uses Dall-e AI to generate a artwork for the Song. Takes an optional argument _prompt_. If no argument is given, ~~it defaults to the Song.prompt attribute~~ it looks for a "small" thematic summary already on the Song object. If one is found this will be engineered into the prompt. If a thematic summary isn't found, or if it is a "large" summary the get_lyric_summary() method will run and the result will be used to build the image generator prompt.

The prompt is constructed using another AI helper function _get_visual_description()_ which prompts the GPT engine to describe an imaginary scene based on the themes provided.

The art generation is achieved by making a call to another AI helper function called _generate_img()_, passing in values for prompt (see above), size and image format from the Song's stored attributes.

If the helper function is unable to generate an image it will print a message and raise ValueError. Subsequently, if the function succeeds but the returned object does not include a "url" or "b64_json" key a ValueError will be raised.

If the image format is set to "url" the image's url will be saved to the **Song.art_url** attribute. This can be opened with the **open_art()** method, or accessed programmatically for use elsewhere. Note that according to OpenAI's documentation a url lasts for 1 hour.
If the image format is set to "b64*json", the image stream will be decoded, saved on the song instance, and the \_save_art()* method will be immediately called, saving the image to disk. If decoding fails, the error will be printed to stdout and a ValueError is raised.

- Song.**open_art**()

If an artwork was generated with the "url" image format, opens the url in the system default web browser.

- Song.**save_art**(_filename="song_art.png"_, _PATH="./"_)

If an artwork was generated with the "b64_json" image format, saves the image to disk. The saved filename defaults to "song_art.png" and saves into the current directory.

- Song.**generate_lyric_suggestion**()

TODO Coming soon!

- Song.**get_lyric_summary**(_size="sm"_)

A method to access the return value from the AI helper function _summarize_lyrics()_. This function uses openAI's davinci-003 model to summarize the main themes in a string of lyrics. The idea is to use this summary as the input to generating an artwork, additional lyrics, or just to have for reference.

Takes an optional parameter _size_ which defaults to "sm". The only alternative is "lg". Anything else will result in a ValueError being raised. All this does is tells the AI, in the case of "sm", to keep the summary to five words or fewer. If "lg" is passed as an argument, the AI will return a more in depth summary of the song's themes.

The summary is used as input to the artwork prompt generator, but will only work if the summary had the "sm" attribute assigned to it. The summary is stored on the song instance at self.lyric_summary and is a dictionary containing two keys: "size" and "themes".

- Song.**get_visual_description**(_themes_)

Calls the AI helper function _create_visual_descriptor()_ which uses the GPT text completion to describe a visual scene based on the themes provided. If calling this method manually, you will need to provide the themes as an argument. This is all automated when generating an image without a prompt, however if you would like to provide the AI with a custom list of themes, you can use this method and pass its return value (a string) to _generate_song_art()_ as the prompt.
