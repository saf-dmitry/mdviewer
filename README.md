

# MDviewer

MDviewer is a cross-platform and editor-agnostic previewer for Markdown files. Use it with your favorite text editor and it updates every time you save.

MDviewer can also be extended to work with just about any processor you need, including Textile, reStructuredText, Wikitext and more.

![](images/screenshot.png)


# Contents

- [Installation](#installation)
- [Configuration](#configuration)
    - [Configuration Files](#configuration-files)
    - [Setting a Markdown Processor](#setting-a-markdown-processor)
- [Usage](#usage)
    - [Opening Files](#opening-files)
    - [Choosing a Style](#choosing-a-style)
    - [Text Zoom](#text-zoom)
    - [Table of Contents](#table-of-contents)
    - [Scroll to Edit](#scroll-to-edit)
    - [Clicking External Links](#clicking-external-links)
    - [Searching](#searching)
    - [Exporting HTML](#exporting-html)
    - [Printing](#printing)
    - [Using Custom Styles](#using-custom-styles)
    - [Using Math Formulas](#using-math-formulas)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
    - [Preview Not Updating](#preview-not-updating)
    - [Scroll to Edit Issue](#scroll-to-edit-issue)
    - [Overall Performance Issue](#overall-performance-issue)
- [Acknowledgments](#acknowledgments)
- [Bugs](#bugs)
- [License](#license)


# Installation

MDviewer requires the following packages to run:

- [Python][python] version 2.7 or higher
- [PyQt4][pyqt4] version 4.8 or higher
- Markdown processor (see the [Setting a Markdown Processor](#setting-a-markdown-processor) section below)


# Configuration


## Configuration Files

By default, MDviewer checks the following places for configuration files, in the following order:

- `$HOME/.config/mdviewer/settings.yml` on macOS and GNU/Linux or `%APPDATA%\mdviewer\settings.yml` on MS Windows
- `settings.yml` in the viewer's root directory

Configuration files are UTF-8-encoded YAML files.


## Setting a Markdown Processor

First, you must specify a Markdown processor in the `processor_path` field of the configuration file. Enter a full path to an executable or script which can return HTML or SVG output on STDOUT and it will be used for Preview and Save operations. Examples of cross-plattform Markdown processors include [pandoc][pandoc] or [MultiMarkdown][multimarkdown].

If the specified processor needs additional arguments besides the file name, specify them in the `processor_args` field, separating each argument with a space, just like you would on the command line. If your process is more complicated than a single command, create a self-contained script, make it executable and point the Markdown processor setting to it. In your scripts you can use the MDviewer-specific environment variables as described in the [Environment Variables](#environment-variables) section.

Configuration file entry example:

    processor_path: /usr/bin/pandoc
    processor_args: --from=markdown --to=html5 --standalone


# Usage


## Opening Files

You can open Markdown files directly using the File > Open menu option. Alternatively, you can give the name of the file as a command-line argument when calling the viewer:

    mdviewer file.md


## Choosing a Style

You can select a style in the Style drop-down menu.


## Text Zoom

You can change the text size using the View menu option.


## Table of Contents

If your document has headings in it, the Goto menu option will be active. Clicking on it will expand the Table of Contents, and clicking the title of a heading will navigate to that section of the preview.


## Scroll to Edit

The "Scroll to Edit" feature keeps track of differences between the latest update and the last, scrolling to the point where you made your most recent changes and highlighting the location of the first change detected.

By default, the scrolling takes place after some delay (1500 ms). You can change this value using the `scroll_delay` field in your configuration file:

    scroll_delay: 500


## Clicking External Links

Clicking an external link in your document's preview will open it in your default browser.


## Searching

The search bar can be accessed with File > Find menu option and allows you to incrementally search through the preview for a word or phrase. Once you search, you can use Next and Previous buttons on the right side of the search bar to navigate forward and backward through additional results.

The buttons on the left side of the search bar allow you to narrow the search down by case sensitivity and wrap the search around the document boundaries.


## Exporting HTML

The File > Save HTML menu option will allow you to save a full HTML document ready for sharing or publishing.


## Printing

The File > Print menu option will bring up a standard print dialog. Here you can select a printer and set available printing options. The preview will be printed based on the currently selected style. Each preview style has its own accompanying print style which modifies type sizes and colors, and displays external links.

You can save the preview as paginated PDF by choosing "Print to File (PDF)" in the drop-down list of available printers.


## Using Custom Styles

If you're familiar with CSS, you can create your own style sheets and copy them to the viewer's `stylesheets` directory. New styles will be added to the Style drop-down menu and named based on the CSS file name.


## Using Math Formulas

You can use [MathJax][mathjax] JavaScrpt library to render inline and displayed LaTeX equations embedded in your documents.

To install MathJax on Debian-based systems such as Ubuntu or Mint, all you need to do is

    sudo apt-get install libjs-mathjax

On UNIX systems where MathJax is not packaged, you can download it from GitHub and extract to `/usr/share/javascript` directory.

Alternatively, you can use a third party [CDN server][mathjax-cdn], where the JavaScript needed for MathJax to work will be loaded at run time. This simplifies the installation and ensures the latest version of the library is always used, but requires an Internet connection at run time.

To enable MathJax support you have to point your Markdown processor or your document template to the `MathJax.js` load script. The exact way depends on your Markdown processor (see the [Setting a Markdown Processor](#setting-a-markdown-processor) section). E.g., in case of MultiMarkdown you can add following to your Markdown document:

    html header: <script type="text/javascript"
        src="/usr/share/javascript/MathJax/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
        </script>

Pandoc provides the `--mathjax[=URL]` command-line option. The URL should point to the `MathJax.js` load script. If an URL is not provided, a link to the [Cloudflare CDN][mathjax-cdn] will be inserted.

    pandoc --from=markdown --to=html5 --standalone \
           --mathjax=/usr/share/javascript/MathJax/MathJax.js?config=TeX-AMS-MML_HTMLorMML


MathJax supports most of the standard LaTeX syntax, as well as some AMS extensions and custom LaTeX macros. See [MathJax TeX and LaTeX Support][mathjax-tex] and [Loading and Configuring MathJax][mathjax-config] pages for details.


# Environment Variables

MDviewer runs the processor in its own shell, meaning standard environment variables are not automatically passed. You can use MDviewer's environment variables to augment your own in your scripts. MDviewer makes the following variables available for use in your shell scripts:

- `MDVIEWER_EXT`: The extension of the file being processed.
- `MDVIEWER_PATH`: The directory part of the path to the file being viewed.

These variables allows you to script different processes based on the type of file being viewed. For example, on a UNIX system you can create a shell script `mdviewer-proc.sh`

    #!/bin/sh

    case "$MDVIEWER_EXT" in
        md | markdown | text )
            pandoc --from=markdown --to=html5 --standalone "$1" ;;
        html | htm | svg )
            cat "$1" ;;
    esac

make in executable and point the Markdown processor setting to it:

    processor_path: mdviewer-proc.sh
    processor_args: ''


# Troubleshooting


## Preview Not Updating

Some text editors don't modify the contents of a file, but replace the original file with a new one having same name but different inode. Replacing a file will delete the old one, so MDviewer will stop watching the file. Many editors can be configured to modify existing file when saving instead of replacing it. Below some configuration tips for popular programming editors.

- Vim: Add following line to your `.vimrc` configuration file:

        set backupcopy=yes

- GNU Emacs: Add following line to your `.emacs` configuration file:

        (setq backup-by-copying t)


## Scroll to Edit Issue

If you are using external JavaScripts, which run asynchronously, you may experience unexpected scrolling behavior. DOM changes can be especially problematic.

In this case you may need to increase the scroll delay value using the `scroll_delay` filed in your configuration file (default is 1500 ms).


## Overall Performance Issue

The rendering performance can vary greatly based on your configuration settings and the document content. There are several factors that can affect rendering speed:

- __Markdown processor.__ Different Markdown processors have different performance, which depends on the type of content you have in your document.

- __Markdown document containing a lot of math formulas.__ The math rendering performance generally depends on the [MathJax][mathjax] configuration options, especially those controlling the output generation. Depending on type and complexity of your math you may consider using [KaTeX][katex] as alternative math renderer.


# Acknowledgments

- Copyright 2013 Matthew Borgerson <mborgerson@gmail.com>
- Copyright 2014 Vova Kolobok <vovkkk@ya.ru>


# Bugs

MDviewer is developed and tested primarily to work on GNU/Linux and other POSIX-compatible platforms. If you find any bugs in MDviewer, please construct a test case or a patch and open a ticket on the [GitHub issue tracker][github-issues].


# License

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.


[python]: https://www.python.org/downloads/

[pyqt4]: https://riverbankcomputing.com/software/pyqt/download

[pandoc]: https://pandoc.org

[multimarkdown]: http://fletcherpenney.net/multimarkdown/

[mathjax]: https://www.mathjax.org/

[katex]: https://katex.org/

[mathjax-cdn]: https://cdnjs.cloudflare.com/ajax/libs/mathjax/

[mathjax-tex]: http://docs.mathjax.org/en/latest/tex.html

[mathjax-config]: http://docs.mathjax.org/en/latest/configuration.html

[github-issues]: https://github.com/saf-dmitry/mdviewer/issues

