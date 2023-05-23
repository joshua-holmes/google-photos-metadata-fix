# Google Photos Metadata Fix

## What is this?

Are your photos out of order when you export them from Google Photos using Google Takeout?

This is because the photos Google exports does not come with the correct metadata embedded in the photos. Instead, the metadata comes in separate JSON files. But that's not very useful to you, is it?

This Python script inserts the correct metadata into each photo from the corresponding JSON file, then cleans up all the JSON files.

This project was inspired by [MetadataFixer.com](https://metadatafixer.com/), which is a paid version of the same thing. I am unaffiliated and wanted a free alternative, so I wrote this script.

## Dependencies

* python3 (sometimes called python)
* pip3 (sometimes called pip)
* git (optional)

## How to use it

To fix your metadata, follow these steps:

1. Your Google Takeout export came in a .zip file. Unzip it in the directory of your choice. Your directory should look like this:
```
/path/to/my-chosen-directory/
    file1.heic
    file1.json
    file2.jpg
    file2.json
    ...
```
Instead of `file1.heic`, etc., yours will probably be a very long name with numbers and letters. I just used the names above as an example.

2. Clone this repo to your machine, then `cd` into it:
```
$ git clone https://github.com/joshua-holmes/google-photos-metadata-fix.git
$ cd google-photos-metadata-fix
```
If you don't have `git`, feel free to download this repo as a zip file using GitHub's green "Code" button above.

3. Run `pip3 install requirements.txt`
4. Run `python3 run.py /path/to/my-chosen-directory/`

That's it! The program will handle the rest.

This program comes with more features! If you want to see them, run `python3 run.py --help`

## Made by
Joshua Holmes<br/>
[jpholmes.com](https://www.jpholmes.com)<br/>
[linkedin.com/in/joshua-phillip-holmes](https://www.linkedin.com/in/joshua-phillip-holmes/)<br/>
[github.com/joshua-holmes](https://github.com/joshua-holmes)<br/>
[joshua.phillip.holmes@gmail.com](mailto:joshua.phillip.holmes@gmail.com)
