#!/usr/bin/env python
# coding: utf8

import sys, os, webbrowser, importlib, itertools, locale, io, subprocess, shutil, urllib.request, urllib.error, yaml

from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport, QtWebKit, QtWebKitWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import QWebPage, QWebView

VERSION = '0.3'

script_dir = os.path.dirname(os.path.realpath(__file__))
stylesheet_dir = os.path.join(script_dir, 'stylesheets')

class App(QtWidgets.QMainWindow):

    @property
    def QSETTINGS(self):
        return QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, 'MDviewer', 'MDviewer')

    def set_window_title(self):
        _path, name = os.path.split(os.path.abspath(self.filename))
        self.setWindowTitle(u'%s – MDviewer' % (name))

    def set_env (self):
        path, name = os.path.split(os.path.abspath(self.filename))
        ext = name.split('.')[-1].lower()
        os.environ['MDVIEWER_EXT'] = ext
        os.environ['MDVIEWER_FILE'] = name
        os.environ['MDVIEWER_ORIGIN'] = path

    def __init__(self, parent=None, filename=''):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.filename = filename or os.path.join(script_dir, u'README.md')

        self.set_env()
        # Settings.print_path()

        # Configure window
        self.set_window_title()
        self.resize(self.QSETTINGS.value('size', QtCore.QSize(800,800)))
        self.move(self.QSETTINGS.value('pos', QtCore.QPoint(50,50)))

        # Activate WebView
        self.web_view = QtWebKitWidgets.QWebView()
        self.setCentralWidget(self.web_view)

        self.scroll_pos = {}

        # Configure and start file watcher thread
        self.thread1 = WatcherThread(self.filename)
        self.thread1.update.connect(self.update)
        self.watcher = QtCore.QFileSystemWatcher([self.filename])
        self.watcher.fileChanged.connect(self.thread1.run)
        self.thread1.start()

        # Restore scroll position
        self.web_view.loadFinished.connect(self.after_update)

        # Set GUI
        self.set_menus()
        self.set_search_bar()

    def update(self, text, warn):
        '''Update Preview.'''

        self.web_view.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

        self.web_view.linkClicked.connect(lambda url: webbrowser.open_new_tab(url.toString()))
        self.web_view.page().setLinkDelegationPolicy(QtWebKitWidgets.QWebPage.DelegateExternalLinks)

        # Save scroll position
        if not self.web_view.page().currentFrame().scrollPosition() == QtCore.QPoint(0,0):
            self.scroll_pos[self.filename] = self.web_view.page().currentFrame().scrollPosition()

        # Update Preview
        self.web_view.setHtml(text, baseUrl=QtCore.QUrl('file:///' + os.path.join(os.getcwd(), self.filename)))

        # Load JavaScript and core CSS
        scr = os.path.join(script_dir, 'mdviewer.js')
        css = os.path.join(script_dir, 'mdviewer.css')
        add_resources = '''
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
        ''' % (scr, css)
        self.web_view.page().currentFrame().evaluateJavaScript(add_resources)

        # Display processor warnings
        if warn:
            QtWidgets.QMessageBox.warning(self, 'Processor message', warn)

    def after_update(self):
        '''Restore scroll position.'''

        try:
            pos = self.scroll_pos[self.filename]
        except KeyError:
            pass
        else:
            self.web_view.page().currentFrame().evaluateJavaScript('window.scrollTo(%s, %s);' % (pos.x(), pos.y()))

    def handle_link_clicked(self, url):
        QDesktopServices.openUrl(url)

    def open_file(self):
        filename, _filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.path.dirname(self.filename))
        if filename != '':
            self.filename = self.thread1.filename = filename
            self.set_env()
            self.set_window_title()
            self.thread1.run()
        else:
            pass

    def save_html(self):
        filename, _filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', os.path.dirname(self.filename))
        if filename != '':
            proc = Settings.get('processor_path', 'pandoc')
            args = Settings.get('processor_args', '')
            args = ('%s' % (args)).split() + [self.filename]
            caller = QtCore.QProcess()
            caller.start(proc, args)
            caller.waitForFinished()
            html = str(caller.readAllStandardOutput(), 'utf8')
            with io.open(filename, 'w', encoding='utf8') as f:
                f.writelines(str(html))
                f.close()
        else:
            pass

    def find(self, text, btn=''):
        page = self.web_view.page()
        back = page.FindFlags(1) if btn is self.prev else page.FindFlags(0)
        case = page.FindFlags(2) if self.case.isChecked() else page.FindFlags(0)
        wrap = page.FindFlags(4) if self.wrap.isChecked() else page.FindFlags(0)
        page.findText('', page.FindFlags(8))
        page.findText(text, back | wrap | case)

    def set_search_bar(self):
        self.search_bar = QtWidgets.QToolBar()

        self.text = QtWidgets.QLineEdit(self)
        self.case = QtWidgets.QCheckBox(u'Case sensitive', self)
        self.wrap = QtWidgets.QCheckBox(u'Wrap', self)
        self.next = QtWidgets.QPushButton(u'\u25b6', self)
        self.prev = QtWidgets.QPushButton(u'\u25c0', self)
        self.done = QtWidgets.QPushButton(u'Done', self)

        def _toggle_btn(btn=''):
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
        self.search_bar.addWidget(self.prev)
        self.search_bar.addWidget(self.next)
        for btn in (self.prev, self.next):
            btn.pressed[()].connect(lambda btn = btn: _toggle_btn(btn))
        self.done.pressed.connect(_hide)
        self.text.textChanged.connect(self.find)

    def show_search_bar(self):
        self.addToolBar(0x8, self.search_bar)
        self.search_bar.show()
        self.text.setFocus()
        self.text.selectAll()

    def print_doc(self):
        dialog = QtPrintSupport.QPrintPreviewDialog()
        dialog.paintRequested.connect(self.web_view.print_)
        dialog.exec_()

    def quit(self, QCloseEvent):
        self.QSETTINGS.setValue('size', self.size())
        self.QSETTINGS.setValue('pos', self.pos())

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

    def show_toc(self):
        self.web_view.page().currentFrame().evaluateJavaScript('(function() {generateTOC();})()')

    @staticmethod
    def set_stylesheet(self, stylesheet='default.css'):
        path = os.path.join(stylesheet_dir, stylesheet)
        url = QtCore.QUrl.fromLocalFile(path)
        self.web_view.settings().setUserStyleSheetUrl(url)

    def about(self):
        msg_about = QtWidgets.QMessageBox(0, 'About MDviewer', u'MDviewer\n\nVersion: %s' % (VERSION), parent=self)
        msg_about.show()

    def set_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')

        for d in (
                {'label': u'&Open...',      'keys': 'Ctrl+O', 'func': self.open_file},
                {'label': u'&Save HTML...', 'keys': 'Ctrl+S', 'func': self.save_html},
                {'label': u'&Find...',      'keys': 'Ctrl+F', 'func': self.show_search_bar},
                {'label': u'&Print...',     'keys': 'Ctrl+P', 'func': self.print_doc},
                {'label': u'&Quit',         'keys': 'Ctrl+Q', 'func': self.quit}
                 ):
            action = QtWidgets.QAction(d['label'], self)
            action.setShortcut(d['keys'])
            action.triggered.connect(d['func'])
            file_menu.addAction(action)

        view_menu = menubar.addMenu('&View')

        for d in (
                {'label': u'Zoom &In',     'keys': 'Ctrl++', 'func': self.zoom_in},
                {'label': u'Zoom &Out',    'keys': 'Ctrl+-', 'func': self.zoom_out},
                {'label': u'&Actual Size', 'keys': 'Ctrl+0', 'func': self.zoom_reset}
                 ):
            action = QtWidgets.QAction(d['label'], self)
            action.setShortcut(d['keys'])
            action.triggered.connect(d['func'])
            view_menu.addAction(action)

        style_menu = menubar.addMenu('&Style')
        style_menu.setStyleSheet('menu-scrollable: 1')
        style_menu.setDisabled(True)

        if os.path.exists(stylesheet_dir):
            sheets = []
            for f in sorted(os.listdir(stylesheet_dir)):
                if not f.endswith('.css'): continue
                a = os.path.splitext(f)[0].replace("&", "&&")
                sheets.append(QtWidgets.QAction(a, self))
                if len(sheets) < 10:
                    sheets[-1].setShortcut('Ctrl+%d' % len(sheets))
                sheets[-1].triggered.connect(
                    lambda x, stylesheet = f: self.set_stylesheet(self, stylesheet))
            group = QtWidgets.QActionGroup(self, exclusive=True)
            for item in sheets:
                item.setCheckable(True)
                action = group.addAction(item)
                style_menu.addAction(action)
            style_menu.setDisabled(False)
            self.set_stylesheet(self, 'default.css')

        help_menu = menubar.addMenu('&Help')

        for d in (
                {'label': u'&About...', 'func': self.about},
                 ):
            action = QtWidgets.QAction(d['label'], self)
            action.triggered.connect(d['func'])
            help_menu.addAction(action)

        # Redefine reload action
        reload_action = self.web_view.page().action(QtWebKitWidgets.QWebPage.Reload)
        reload_action.setShortcut(QtGui.QKeySequence.Refresh)
        reload_action.triggered.connect(self.thread1.run)
        self.web_view.addAction(reload_action)

        # Define additional shortcuts
        QtWidgets.QShortcut('j', self, activated = self.scroll_down)
        QtWidgets.QShortcut('k', self, activated = self.scroll_up)
        QtWidgets.QShortcut('t', self, activated = self.show_toc)

class WatcherThread(QtCore.QThread):
    update = pyqtSignal(str, str)

    def __init__(self, filename):
        QtCore.QThread.__init__(self)
        self.filename = filename

    def run(self):
        html, warn = self.processor_rules()
        self.update.emit(html, warn)

    def processor_rules(self):
        proc = Settings.get('processor_path', 'pandoc')
        args = Settings.get('processor_args', '')
        args = ('%s' % (args)).split() + [self.filename]
        html = ''; warn = ''
        if shutil.which(proc) is not None:
            caller = QtCore.QProcess()
            caller.start(proc, args)
            caller.waitForFinished()
            html = str(caller.readAllStandardOutput(), 'utf8')
            warn = str(caller.readAllStandardError(), 'utf8')
        else:
            warn = u'Executable not found: %s' % (proc)
        return (html, warn)

class Settings:
    def __init__(self):
        if os.name == 'nt':
            self.user_source = os.path.join(os.getenv('APPDATA'), 'mdviewer', 'settings.yml')
        else:
            self.user_source = os.path.join(os.getenv('HOME'), '.config', 'mdviewer', 'settings.yml')
        self.app_source = os.path.join(script_dir, 'settings.yml')
        self.settings_file = self.user_source if os.path.exists(self.user_source) else self.app_source
        self.reload_settings()

    def reload_settings(self):
        with io.open(self.settings_file, 'r', encoding='utf8') as f:
            self.settings = yaml.safe_load(f)

    @classmethod
    def get(cls, key, default_value):
        return cls().settings.get(key, default_value)

    @classmethod
    def print_path(cls):
        print('Settings: %s' % cls().settings_file)

def main():
    app = QApplication(sys.argv)
    if len(sys.argv) != 2:
        window = App()
    else:
        window = App(filename=sys.argv[1])
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

