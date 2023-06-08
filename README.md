# Google Photos Metadata Fix

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
* git (optional)

## How to use it

To fix your metadata, follow these steps:

1. Clone this repo to your machine, then `cd` into it:
```
$ git clone https://github.com/joshua-holmes/google-photos-metadata-fix.git
$ cd google-photos-metadata-fix
```
If you don't have `git`, feel free to download this repo as a zip file using GitHub's green "Code" button above.

2. Run `pip3 install requirements.txt` to install Python dependencies for this project.
3. Run `python3 run.py /path/to/my/directory/takeout.zip` where `takeout.zip` is the zip file that Google gives you when you download the export.
4. You should now see a new `takeout/` directory right next to your `takeout.zip` file that you downloaded from Google.
```
/path/to/my/directory/
    takeout/
    takeout.zip
```
Feel free to delete the `takeout.zip` file to conserve space! All the photos from `takeout.zip` have already been extracted, had the metadata applied and saved in the new `takeout/` directory.

You can also extract the directory yourself and run the script on `/path/to/my/directory/takeout/`

That's it!

## Made by
Joshua Holmes<br/>
[jpholmes.com](https://www.jpholmes.com)<br/>
[linkedin.com/in/joshua-phillip-holmes](https://www.linkedin.com/in/joshua-phillip-holmes/)<br/>
[github.com/joshua-holmes](https://github.com/joshua-holmes)<br/>
[joshua.phillip.holmes@gmail.com](mailto:joshua.phillip.holmes@gmail.com)
