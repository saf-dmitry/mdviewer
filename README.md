

# MDviewer

MDviewer is a cross-platform and editor-agnostic previewer for Markdown files. Use it with your favorite text editor and it updates every time you save. In applications that automatically save in the background, the Preview will be updated at save intervals as you type.

MDviewer can also be extended to work with just about any processor you need, including Textile, reStructuredText, MediaWiki, AsciiDoc, Graphviz and more.

![](images/screenshot.png)


# Contents

- [Installation](#installation)
- [Configuration](#configuration)
    - [Configuration Files](#configuration-files)
    - [Setting a Markdown Processor](#setting-a-markdown-processor)
- [Basic Usage](#basic-usage)
    - [Opening Files](#opening-files)
    - [Navigating Preview](#navigating-preview)
    - [Choosing a Style](#choosing-a-style)
    - [Zooming In and Out](#zooming-in-and-out)
    - [Clicking External Links](#clicking-external-links)
    - [Searching](#searching)
    - [Exporting HTML](#exporting-html)
    - [Printing](#printing)
- [Advanced Usage](#advanced-usage)
    - [Adding Custom Styles](#adding-custom-styles)
    - [Using Math Formulas](#using-math-formulas)
    - [Evaluating Environment Variables](#evaluating-environment-variables)
- [Troubleshooting](#troubleshooting)
    - [Preview Not Updating](#preview-not-updating)
    - [Overall Performance Issue](#overall-performance-issue)
- [Acknowledgments](#acknowledgments)
- [Bugs](#bugs)
- [License](#license)


# Installation

MDviewer requires the following packages to run:

- [Python 2][python] version 2.7 or higher
- [PyQt4][pyqt4] version 4.8 or higher
- Markdown processor (see the [Setting a Markdown Processor](#setting-a-markdown-processor) section below)


# Configuration


## Configuration Files

MDviewer stores all of its configuration data in YAML files which have the `.yml` extension and use the UTF-8 encoding.

By default, MDviewer checks the following places for configuration files, in the following order:

1. `$HOME/.config/mdviewer/settings.yml` on macOS and GNU/Linux or `%APPDATA%\mdviewer\settings.yml` on MS Windows
2. `settings.yml` in the application's root directory

A path to the configuration file being used is printed to STDOUT during application's startup.

Note: In general, you should place your personal settings in `$HOME/.config/mdviewer/settings.yml` (or `%APPDATA%\mdviewer\settings.yml`), so they will be preserved between software updates.


## Setting a Markdown Processor

First, you must specify a Markdown processor in the `processor_path` field of the configuration file. Enter a full path to an executable or script which can return HTML or SVG output on STDOUT and it will be used for Preview and Save operations. Examples of cross-plattform Markdown processors include [pandoc][pandoc], [PHP Markdown Extra][php-markdown-extra], or [MultiMarkdown][multimarkdown].

If the specified processor needs additional arguments besides the file name, specify them in the `processor_args` field, separating each argument with a space, just like you would on the command line. If your process is more complicated than a single command, create a self-contained script, make it executable and point the Markdown processor setting to it. In your scripts you can use the MDviewer-specific environment variables as described in the [Evaluating Environment Variables](#evaluating-environment-variables) section.

Configuration file entry example:

    processor_path: /usr/bin/pandoc
    processor_args: --from=markdown --to=html5 --standalone


# Basic Usage


## Opening Files

You can open Markdown files directly using the "File > Open" menu option. If a file is currently being displayed it will be closed. Alternatively, you can give the path and name of a particular file as a command-line argument to open that file immediately upon viewer's startup:

    mdviewer file.md


## Navigating Preview

There are multiple ways of scrolling the viewing area. One is to use the Up Arrow and Down Arrow keys. You may also use the scrollbar, your mousewheel or the Page Up and Page Down keys.

If your document has headings in it, the "Goto" drop-down menu will be active. Clicking on it will expand the Table of Contents, and clicking the title of a heading will navigate to that section of the Preview.


## Choosing a Style

You can select a preview and print style in the "Style" drop-down menu. You can add your own styles as described in the [Adding Custom Styles](#adding-custom-styles) section.


## Zooming In and Out

You can increase or decrease the magnification of the document view using the "View" menu options.

Note: Depending on the selected style zooming will change the size of everything on the Preview, including text and images, or just the size of the font.


## Clicking External Links

Clicking an external link in your document's Preview will open it in your default browser.


## Searching

The search bar on the bottom of the viewing area can be accessed with the "File > Find" menu option and allows you to incrementally search through the Preview for a word or phrase. Once you search, you can use "Next" and "Previous" buttons on the right side of the search bar to navigate forward and backward through additional results.

The buttons on the left side of the search bar allow you to narrow the search down by case sensitivity and wrap the search around the document boundaries.


## Exporting HTML

The "File > Save HTML" menu option will allow you to save a full HTML document ready for sharing or publishing.


## Printing

The "File > Print" menu option will bring up a standard print dialog. Here you can select a printer and set available printing options. The Preview will be printed based on the currently selected style. Each preview style has its own accompanying print style which modifies type sizes and colors, and displays external links.

You can save the Preview as paginated PDF by choosing "Print to File (PDF)" in the drop-down list of available printers.


# Advanced Usage


## Adding Custom Styles

If you're familiar with CSS, you can create your own style sheets and copy them to the MDviewer's `stylesheets` directory. New styles will be added to the "Style" drop-down menu and named based on the CSS file name.

All CSS3 options that work in WebKit will work in MDviewer. See existing style sheets in the application's `stylesheets` directory for details.


## Using Math Formulas

You can use [MathJax][mathjax] JavaScrpt library to render inline and displayed LaTeX equations embedded in your documents.

To install MathJax on Debian-based systems such as Ubuntu or Mint, all you need to do is

    sudo apt-get install libjs-mathjax

On UNIX-like systems where MathJax is not packaged, you can download it from [GitHub][mathjax-github] and extract to `/usr/share/javascript/` directory.

Alternatively, you can use a third party CDN server, where the JavaScript needed for MathJax to work will be loaded at run time. This simplifies the installation and ensures the latest version of the library is always used, but requires an Internet connection at run time.

To enable MathJax support you have to point your Markdown processor or your document template to the `MathJax.js` load script. The exact way depends on your Markdown processor (see the [Setting a Markdown Processor](#setting-a-markdown-processor) section). E.g., in case of MultiMarkdown you can add following metadata directly to your Markdown document:

    html header: <script type="text/javascript"
        src="/usr/share/javascript/MathJax/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
        </script>

Pandoc provides the `--mathjax[=URL]` command-line option. The URL should point to the `MathJax.js` load script. If an URL is not provided, a link to the Cloudflare CDN will be inserted.

    pandoc --from=markdown --to=html5 --standalone \
           --mathjax=/usr/share/javascript/MathJax/MathJax.js?config=TeX-AMS-MML_HTMLorMML


MathJax supports most of the standard TeX and LaTeX math syntax, as well as some AMS and other LaTeX extensions and custom macros. See [MathJax TeX and LaTeX Support][mathjax-tex] and [Loading and Configuring MathJax][mathjax-config] pages for details. In the MDviewer's `extras/` directory you can find an example of MathJax's local configuration file, which you can use as a starting point for your own configuration.


## Evaluating Environment Variables

MDviewer runs the processor in its own shell, meaning standard environment variables are not automatically passed. You can use MDviewer's environment variables to augment your own in your scripts. MDviewer makes the following variables available for use in your shell scripts:

- `MDVIEWER_FILE`: The name of the file being viewed
- `MDVIEWER_EXT`: The extension of the file being viewed
- `MDVIEWER_ORIGIN`: The location (base directory) of the file being viewed

These variables allows you to script different processes based on the type of file being viewed. For example, on a UNIX-like system you can create a shell script `mdviewer-proc.sh`

    #!/bin/sh

    case "$MDVIEWER_EXT" in
        md | markdown | text )
            pandoc --from=markdown --to=html5 --standalone "$1" ;;
        rst | rest )
            pandoc --from=rst --to=html5 --standalone "$1" ;;
        dot )
            dot -Kdot -Tsvg "$1" ;;
        html | htm | svg )
            cat "$1" ;;
    esac

make in executable and point the Markdown processor setting to it:

    processor_path: mdviewer-proc.sh
    processor_args: ''


# Troubleshooting


## Preview Not Updating

Some text editors will save by writing to an alternate file and then renaming it over the original one. The original file is removed when the new file has been successfully written. Because the original file is deleted, MDviewer will get confused and stop watching the file.

Many editors can be configured to update existing file in place when saving instead of replacing it. Below some configuration tips for popular programming editors.

- __Vim:__ Add following line to your `.vimrc` configuration file:

        set backupcopy=yes

- __GNU Emacs:__ Add following line to your `.emacs` configuration file:

        (setq backup-by-copying t)

- __Sublime Text:__ Add following line to your `Preferences.sublime-settings` configuration file:

        "atomic_save": false


## Overall Performance Issue

The rendering performance can vary greatly based on your configuration settings and the document content. There are several factors that can affect rendering speed:

- __Markdown processor.__ Different Markdown processors have different performance, which depends on the type of content you have in your document.

- __Markdown documents containing a lot of math expressions.__ The math rendering performance generally depends on the [MathJax][mathjax] configuration, especially the output processor options. Depending on type and complexity of your math you may consider using [KaTeX][katex] as alternative LaTeX math renderer.


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

[php-markdown-extra]: https://michelf.ca/projects/php-markdown/extra/

[multimarkdown]: http://fletcherpenney.net/multimarkdown/

[mathjax]: https://www.mathjax.org/

[mathjax-github]: https://github.com/mathjax/MathJax

[mathjax-tex]: http://docs.mathjax.org/en/latest/tex.html

[mathjax-config]: http://docs.mathjax.org/en/latest/configuration.html

[katex]: https://katex.org/

[github-issues]: https://github.com/saf-dmitry/mdviewer/issues

