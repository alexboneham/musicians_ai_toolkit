import pytest
import argparse

from project import (
    parse_arguments,
    song_info,
    print_lyrics,
    generate_img,
    summarize_lyrics,
    create_visual_descriptor,
)
from project import Song


def test_parse_arguments():
    """Run argument parser with correct and incorrect options"""
    assert parse_arguments(
        [
            "--size",
            "lg",
            "--format",
            "b64_json",
            "-f",
            "data/lionel_hello.txt",
            "--name",
            "Hello",
        ]
    ) == argparse.Namespace(
        size="lg", format="b64_json", f="data/lionel_hello.txt", name="Hello"
    )

    with pytest.raises(SystemExit):
        parse_arguments(["--size", "big"])

    with pytest.raises(SystemExit):
        parse_arguments(["--format", "web"])


# Initialize song for use in tests
s = Song("./data/lionel_hello.txt")


def test_song_info():
    assert song_info(s) == {"print": s.__str__(), "song": s}


def test_print_lyrics():
    assert print_lyrics(s) == {"print": s.lyrics, "song": s}


def test_generate_img():
    with pytest.raises(ValueError):
        generate_img("", "sm", "url")

    with pytest.raises(ValueError):
        generate_img("A cat in a hat", "big", "url")

    with pytest.raises(ValueError):
        generate_img("A cat in a hat", "sm", "web")

    with pytest.raises(TypeError):
        generate_img()


def test_summarize_lyrics():
    with pytest.raises(ValueError):
        summarize_lyrics("These are the lyrics", "big")

    with pytest.raises(TypeError):
        summarize_lyrics()


def test_create_visual_descriptor():
    with pytest.raises(TypeError):
        create_visual_descriptor()

    with pytest.raises(RuntimeError):
        # Raises error because API is not configured
        create_visual_descriptor("Love, faith, redemption")
