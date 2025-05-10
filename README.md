# Google Photos Metadata Fix

## Announcement: GUI Version

This project will eventually be deprecated and replaced with a GUI version called [Google Photos Takeout Util](https://github.com/joshua-holmes/google-photos-takeout-util). This project has been useful to a lot of people, but can be difficult to use if you're unfamiliar with Python environments (which are unnecessarily complicated). So keep an eye out for that!

## Disclaimers

This project has no affiliation with Google and is not endorsed by them. This is my own personal project that I made to solve a problem I had with Google Photos.

This project is also currently in development and might contain bugs. You are welcome to try it though, it may work for you! If it does not and you are interested in helping out, please create an "issue" for this project here in GitHub if you find a bug.

## What is this?

Are your photos out of order when you export them from Google Photos using Google Takeout?

This is because the photos Google exports does not come with the correct metadata embedded in the photos. Instead, the metadata comes in separate JSON files. But that's not very useful to you, is it?

This Python script inserts the correct metadata into each photo from the corresponding JSON file, then cleans up all the JSON files.

This script also converts all HEIC photos into JPEG photos, which is a more common file format for pictures. HEIC photos are an Apple-only file format for photos that will not be viewable on all devices. Any device will be able to view JPEG photos.

This project was inspired by [MetadataFixer.com](https://metadatafixer.com/), which is a paid version of the same thing. I am unaffiliated and wanted a free alternative, so I wrote this script.

## Dependencies

* python3 (sometimes called python)
* pip3 (sometimes called pip)
* poetry (you can install this with `pip3 install poetry` after you install pip3)
* git (optional)

## How to use it

To fix your metadata, follow these steps:

1. Clone this repo to your machine, then `cd` into it:
```
$ git clone https://github.com/joshua-holmes/google-photos-metadata-fix.git
$ cd google-photos-metadata-fix
```
If you don't have `git`, feel free to download this repo as a zip file using GitHub's green "Code" button above.

2. Run `python3 -m venv .venv && source ./.venv/bin/activate` to enter into a virtual environment. This just ensures your dependencies are installed in a known location in case you want to delete them after using this script. This "known location" will be listed in the terminal after you run this command.
3. Run `poetry install` to install Python dependencies for this project.
4. Run `python3 run.py /path/to/my/directory/takeout.zip` where `takeout.zip` is the zip file that Google gives you when you download the export.
5. You should now see a new `takeout/` directory right next to your `takeout.zip` file that you downloaded from Google.
```
/path/to/my/directory/
    takeout/
    takeout.zip
```
Feel free to delete the `takeout.zip` file to conserve space! All the photos from `takeout.zip` have already been extracted, had the metadata applied and saved in the new `takeout/` directory.

Alternatively, you can extract the directory yourself and run the script on `/path/to/my/directory/takeout/` if you prefer to run the script on an extracted directory instead of a zip file.

That's it!

## Development
If you want to help make this project better, thank you! To utilize this repos testing environment:

1. (Optional) Run `poetry config virtualenvs.in-project true` to set Poetry to install the dependencies here in the project's repo, instead of in `~/.cache` somewhere. Be aware that this is a global Poetry setting. Lookup the Poetry documentation for more options if you desire.

2. Run `poetry install` to install dependencies

3. Run `poetry run pytest` to run all tests. `poetry run pytest ./src` will run only unit tests. `poetry run pytest ./tests` will run only integration tests. All tests are saved in a `**/tests` directory.

After you make changes in your own forked repo, feel free to make a pull request!

## Made by
Joshua Holmes<br/>
[jpholmes.com](https://www.jpholmes.com)<br/>
[linkedin.com/in/joshua-phillip-holmes](https://www.linkedin.com/in/joshua-phillip-holmes/)<br/>
[github.com/joshua-holmes](https://github.com/joshua-holmes)<br/>
[joshua.phillip.holmes@gmail.com](mailto:joshua.phillip.holmes@gmail.com)
