#!/usr/bin/env python
# coding: utf8

import sys, os, io, shutil, yaml
# import locale, importlib, subprocess

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKit, QtWebKitWidgets, QtPrintSupport
from PyQt5.QtCore import *
from PyQt5.QtGui import QDesktopServices, QIcon, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtWidgets import QToolBar, QCheckBox, QPushButton, QLineEdit, QAction, QActionGroup, QShortcut
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtPrintSupport import QPrintPreviewDialog

VERSION = "0.4"

app_dir = os.path.dirname(os.path.realpath(__file__))
css_dir = os.path.join(app_dir, "stylesheets")

class App(QMainWindow):

    @property
    def QSETTINGS(self):
        return QSettings(QSettings.IniFormat, QSettings.UserScope, "mdviewer", "session")

    def __init__(self, parent = None, filename = ""):
        QMainWindow.__init__(self, parent)
        self.filename = filename or os.path.join(app_dir, u"README.md")

        # Set environment variables
        self.set_env()

        # Configure Preview window
        self.set_window_title()
        self.resize(self.QSETTINGS.value("size", QSize(800,400)))
        self.move(self.QSETTINGS.value("pos", QPoint(0,0)))

        # Activate WebView
        self.web_view = QWebView()
        self.setCentralWidget(self.web_view)

        self.scroll_pos = {}

        # Configure and start file watcher thread
        self.thread1 = WatcherThread(self.filename)
        self.thread1.update.connect(self.update)
        self.watcher = QFileSystemWatcher([self.filename])
        self.watcher.fileChanged.connect(self.thread1.run)
        self.thread1.run()

        self.web_view.loadFinished.connect(self.after_update)

        # Get style sheet
        self.stylesheet = self.QSETTINGS.value("stylesheet", "default.css")

        # Set GUI menus and toolbars
        self.set_menus()
        self.set_search_bar()

    def set_env (self):
        path, name = os.path.split(os.path.abspath(self.filename))
        ext = name.split(".")[-1].lower()
        os.environ["MDVIEWER_EXT"] = ext
        os.environ["MDVIEWER_FILE"] = name
        os.environ["MDVIEWER_ORIGIN"] = path

    def set_window_title(self):
        _path, name = os.path.split(os.path.abspath(self.filename))
        self.setWindowTitle(u"%s – MDviewer" % (name))

    def update(self, text, warn):
        "Update Preview."

        self.web_view.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        # Configure link behavior
        self.web_view.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.web_view.linkClicked.connect(lambda url: self.handle_link_clicked(url))

        # Save scroll position
        if not self.web_view.page().currentFrame().scrollPosition() == QPoint(0,0):
            self.scroll_pos[self.filename] = self.web_view.page().currentFrame().scrollPosition()

        # Update Preview
        self.web_view.setHtml(text, baseUrl = QUrl.fromLocalFile(os.path.join(os.getcwd(), self.filename)))

        # Load JavaScript and core CSS
        scr = os.path.join(app_dir, "mdviewer.js")
        css = os.path.join(app_dir, "mdviewer.css")
        add_resources = """
        (function() {
            var scr = document.createElement("script");
            scr.type = "text/javascript";
            scr.src = "%s";
            document.head.appendChild(scr);
            var css = document.createElement("link");
            css.rel = "stylesheet";
            css.href = "%s";
            document.head.appendChild(css);
        })()
        """ % (scr, css)
        self.web_view.page().currentFrame().evaluateJavaScript(add_resources)

        # Display processor warnings
        if warn: QMessageBox.warning(self, "Processor message", warn)

    def after_update(self):
        "Restore scroll position."

        try:
            pos = self.scroll_pos[self.filename]
        except KeyError:
            pass
        else:
            self.web_view.page().currentFrame().evaluateJavaScript("window.scrollTo(%s, %s);" % (pos.x(), pos.y()))

    def open_file(self):
        filename, _filter = QFileDialog.getOpenFileName(self, "Open File", os.path.dirname(self.filename))
        if filename != "":
            self.filename = self.thread1.filename = filename
            self.set_env()
            self.set_window_title()
            self.thread1.run()
        else:
            pass

    def save_html(self):
        filename, _filter = QFileDialog.getSaveFileName(self, "Save File", os.path.dirname(self.filename))
        if filename != "":
            proc = Settings.get("processor_path", "pandoc")
            args = Settings.get("processor_args", "")
            args = ("%s" % (args)).split() + [self.filename]
            caller = QProcess()
            caller.start(proc, args)
            caller.waitForFinished()
            html = str(caller.readAllStandardOutput(), "utf8")
            with io.open(filename, "w", encoding = "utf8") as f:
                f.writelines(html)
                f.close()
        else:
            pass

    def find(self, text, btn = ""):
        page = self.web_view.page()
        back = page.FindFlags(1) if btn is self.prev else page.FindFlags(0)
        case = page.FindFlags(2) if self.case.isChecked() else page.FindFlags(0)
        wrap = page.FindFlags(4) if self.wrap.isChecked() else page.FindFlags(0)
        page.findText("", page.FindFlags(8))
        page.findText(text, back | wrap | case)

    def set_search_bar(self):
        self.search_bar = QToolBar()
        self.search_bar.setMovable(False)
        self.search_bar.setFloatable(False)
        self.search_bar.layout().setSpacing(1)

        self.text = QLineEdit(self)
        self.text.setClearButtonEnabled(True)
        self.text.setPlaceholderText(u"Search")
        self.case = QCheckBox(u"Case sensitive", self)
        self.wrap = QCheckBox(u"Wrap", self)
        self.next = QPushButton(u"Next", self)
        self.next.setToolTip(u"Find next")
        self.next.setShortcut(QKeySequence("Return"))
        self.next.setDisabled(True)
        self.prev = QPushButton(u"Previous", self)
        self.prev.setToolTip(u"Find previous")
        self.prev.setShortcut(QKeySequence("Shift+Return"))
        self.prev.setDisabled(True)
        self.done = QPushButton(u"Done", self)
        self.done.setToolTip(u"Hide Search bar")
        self.done.setShortcut(QKeySequence("Esc"))

        def _enable_nav():
            if self.text.text() == "":
                self.next.setDisabled(True)
                self.prev.setDisabled(True)
            else:
                self.next.setDisabled(False)
                self.prev.setDisabled(False)

        def _toggle_btn(btn = ""):
            self.text.setFocus()
            self.find(self.text.text(), btn)

        def _hide():
            if self.search_bar.isVisible():
                self.search_bar.hide()

        self.search_bar.addWidget(self.done)
        self.search_bar.addSeparator()
        self.search_bar.addWidget(self.case)
        self.search_bar.addWidget(self.wrap)
        self.search_bar.addWidget(self.text)
        self.search_bar.addSeparator()
        self.search_bar.addWidget(self.next)
        self.search_bar.addWidget(self.prev)
        for btn in (self.prev, self.next):
            btn.pressed[()].connect(lambda btn = btn: _toggle_btn(btn))
        self.done.pressed.connect(_hide)
        self.text.textChanged.connect(self.find)
        self.text.textChanged.connect(_enable_nav)

    def show_search_bar(self):
        self.addToolBar(0x8, self.search_bar)
        self.search_bar.show()
        self.text.setFocus()
        self.text.selectAll()

    def print_doc(self):
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self.web_view.print_)
        dialog.exec_()

    def quit(self, QCloseEvent):
        self.QSETTINGS.setValue("size", self.size())
        self.QSETTINGS.setValue("pos", self.pos())
        self.QSETTINGS.setValue("stylesheet", self.stylesheet)

        QtWidgets.qApp.quit()

    def zoom_in(self):
        self.web_view.setZoomFactor(self.web_view.zoomFactor()+.1)

    def zoom_out(self):
        self.web_view.setZoomFactor(self.web_view.zoomFactor()-.1)

    def zoom_reset(self):
        self.web_view.setZoomFactor(1)

    def scroll_down(self):
        self.web_view.page().currentFrame().scroll(0, +self.web_view.page().viewportSize().height())

    def scroll_up(self):
        self.web_view.page().currentFrame().scroll(0, -self.web_view.page().viewportSize().height())

    def toggle_toc(self):
        self.web_view.page().currentFrame().evaluateJavaScript("toggleTOC()")

    def handle_link_clicked(self, url):
        if url.isLocalFile():
            if url.toLocalFile() == os.path.join(os.getcwd(), self.filename) and url.hasFragment():
                self.web_view.page().currentFrame().scrollToAnchor(url.fragment())
                return
            else:
                QDesktopServices.openUrl(url)
        else:
            QDesktopServices.openUrl(url)

    @staticmethod
    def set_stylesheet(self, stylesheet = "default.css"):
        path = os.path.join(css_dir, stylesheet)
        url = QUrl.fromLocalFile(path)
        self.web_view.settings().setUserStyleSheetUrl(url)
        self.stylesheet = stylesheet

    def about(self):
        msg_about = QMessageBox(0, "About MDviewer", u"MDviewer\n\nVersion: %s" % (VERSION), parent = self)
        msg_about.show()

    def set_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        for d in (
                {"name": u"&Open...",      "shct": "Ctrl+O", "func": self.open_file},
                {"name": u"&Save HTML...", "shct": "Ctrl+S", "func": self.save_html},
                {"name": u"&Find...",      "shct": "Ctrl+F", "func": self.show_search_bar},
                {"name": u"&Print...",     "shct": "Ctrl+P", "func": self.print_doc},
                {"name": u"&Quit",         "shct": "Ctrl+Q", "func": self.quit}
                 ):
            action = QAction(d["name"], self)
            action.setShortcut(QKeySequence(d["shct"]))
            action.triggered.connect(d["func"])
            file_menu.addAction(action)

        view_menu = menubar.addMenu("&View")

        for d in (
                {"name": u"Zoom &In",     "shct": "Ctrl++", "func": self.zoom_in},
                {"name": u"Zoom &Out",    "shct": "Ctrl+-", "func": self.zoom_out},
                {"name": u"&Actual Size", "shct": "Ctrl+0", "func": self.zoom_reset}
                 ):
            action = QAction(d["name"], self)
            action.setShortcut(QKeySequence(d["shct"]))
            action.triggered.connect(d["func"])
            view_menu.addAction(action)

        style_menu = menubar.addMenu("&Style")
        style_menu.setStyleSheet("menu-scrollable: 1")
        style_menu.setDisabled(True)

        if os.path.exists(css_dir):
            files = sorted(os.listdir(css_dir))
            files = [f for f in files if f.endswith(".css")]
            if len(files) > 0:
                style_menu.setDisabled(False)
                group = QActionGroup(self, exclusive = True)
                for i, f in enumerate(files, start = 1):
                    name = os.path.splitext(f)[0].replace("&", "&&")
                    action = group.addAction(QtWidgets.QAction(name, self))
                    action.triggered.connect(
                        lambda x, stylesheet = f: self.set_stylesheet(self, stylesheet))
                    if i < 10: action.setShortcut(QKeySequence("Ctrl+%d" % i))
                    action.setCheckable(True)
                    style_menu.addAction(action)
                    if f == self.stylesheet: action.trigger()

        help_menu = menubar.addMenu("&Help")

        for d in (
                {"name": u"&About...", "func": self.about},
                 ):
            action = QAction(d["name"], self)
            action.triggered.connect(d["func"])
            help_menu.addAction(action)

        # Redefine reload action
        reload_action = self.web_view.page().action(QWebPage.Reload)
        reload_action.setShortcut(QKeySequence.Refresh)
        reload_action.triggered.connect(self.thread1.run)
        self.web_view.addAction(reload_action)

        # Define additional shortcuts
        QShortcut(QKeySequence("j"), self, activated = self.scroll_down)
        QShortcut(QKeySequence("k"), self, activated = self.scroll_up)
        QShortcut(QKeySequence("t"), self, activated = self.toggle_toc)

    def closeEvent(self, event):
        self.quit(event)
        event.accept()

class WatcherThread(QThread):
    update = pyqtSignal(str, str)

    def __init__(self, filename):
        QThread.__init__(self)
        self.filename = filename

    def run(self):
        html, warn = self.processor_rules()
        self.update.emit(html, warn)

    def processor_rules(self):
        proc = Settings.get("processor_path", "pandoc")
        args = Settings.get("processor_args", "")
        args = args.split() + [self.filename]
        html = ""; warn = ""
        if shutil.which(proc) is not None:
            caller = QProcess()
            caller.start(proc, args)
            caller.waitForFinished()
            html = str(caller.readAllStandardOutput(), "utf8")
            warn = str(caller.readAllStandardError(), "utf8")
        else:
            warn = u"Executable not found: %s" % (proc)
        return (html, warn)

class Settings:
    def __init__(self):
        if os.name == "nt":
            self.user_source = os.path.join(os.getenv("APPDATA"), "mdviewer", "settings.yml")
        else:
            self.user_source = os.path.join(os.getenv("HOME"), ".config", "mdviewer", "settings.yml")
        self.app_source = os.path.join(app_dir, "settings.yml")
        self.settings_file = self.user_source if os.path.exists(self.user_source) else self.app_source
        self.load_settings()

    def load_settings(self):
        with io.open(self.settings_file, "r", encoding = "utf8") as f:
            self.settings = yaml.safe_load(f)

    @classmethod
    def get(cls, key, default_value):
        return cls().settings.get(key, default_value)

    @classmethod
    def print_path(cls):
        print("Settings: %s" % cls().settings_file)

def main():
    app = QApplication(sys.argv)
    if len(sys.argv) != 2:
        window = App()
    else:
        window = App(filename = sys.argv[1])
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

