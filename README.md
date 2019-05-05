# Autotile Generator
Creates 3x3 Wang Tiles tileset using a simple template file.

# Getting Started
It will convert from the following template:

![Template](/template.png)

Into a nicely designed tileset file ready for auto-tiling:

![Autotile 7x7](/sample_8x6_autotile.png)
![Autotile 7x8](/sample_7x7_autotile.png)

# Prerequisites
* [Python 3.x](https://www.python.org/downloads/)
* [Python Pillow library](https://pillow.readthedocs.io/en/5.1.x/installation.html) (pip install pillow)

# Installation
Clone the repository `https://github.com/FabriceLing/autotile.git` and you are ready to go.

# Usage
You will need to create a template file. Only 5 tiles are needed and a default template is provided. The template needs to include:
* A tile with all corners `empty`
* A tile showing a `vertical` path.
* A tile showing a `horizontal` path.
* A tile showing path both `vertical` and `horizontal`.
* A tile that is `full`.

The `height` of the template file will define the size of the cell. The `width` must be 5 times the `height`.

With your template file ready, open a command line window, navigate to the folder you saved the script (and the template file) and run the command

```shell
$ python autotile.py
```

By default, it will use a template file named `template.png` and create a tileset file named `autotile.png`. You can change those settings.

## Command line options

```shell
  -h, --help         show this help message and exit
  -s template.png    select a template file
  -o autotiles.png   select a output file
  -l layout7x7.json  select a layout template
```

# License
This tool is made available under the [MIT License](https://opensource.org/licenses/mit-license.php).

# Acknowledgments
* [Blob Tileset](http://www.cr31.co.uk/stagecast/wang/blob.html)
* [caeles seamless tileset template II](https://opengameart.org/content/seamless-tileset-template-ii)
* [AutoTile Generator](https://github.com/HeartoLazor/autotile_generator)