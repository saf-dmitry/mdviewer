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
        fpath, fname = os.path.split(os.path.abspath(self.filename))
        self.setWindowTitle(u'%s – MDviewer' % (fname))

    def set_env (self):
        fpath, fname = os.path.split(os.path.abspath(self.filename))
        fext = fname.split('.')[-1].lower()
        os.environ["MDVIEWER_EXT"] = fext
        os.environ["MDVIEWER_FILE"] = fname
        os.environ["MDVIEWER_ORIGIN"] = fpath

    def __init__(self, parent=None, filename=''):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.filename = filename or os.path.join(script_dir, u'README.md')

        self.set_env()
        Settings.print_path()

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
        self.set_search_panel()

    def update(self, text, warn):
        '''Update document view.'''

        # Set WebView attributes
        self.web_view.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

        # Set link policy
        self.web_view.linkClicked.connect(lambda url: webbrowser.open_new_tab(url.toString()))
        self.web_view.page().setLinkDelegationPolicy(QtWebKitWidgets.QWebPage.DelegateExternalLinks)

        # Save scroll position
        if not self.web_view.page().currentFrame().scrollPosition() == QtCore.QPoint(0,0):
            self.scroll_pos[self.filename] = self.web_view.page().currentFrame().scrollPosition()

        # Update document
        self.web_view.setHtml(text, baseUrl=QtCore.QUrl('file:///' + os.path.join(os.getcwd(), self.filename)))

        # Load JavaScript and core CSS
        scr = os.path.join(script_dir, 'mdviewer.js')
        css = os.path.join(script_dir, 'mdviewer.css')
        addresources = '''
        (function() {
        scr = document.createElement('script');
        scr.type = 'text/javascript';
        scr.src = '%s'
        css = document.createElement('link');
        css.rel = 'stylesheet';
        css.href = '%s'
        document.head.appendChild(scr);
        document.head.appendChild(css);
        })()
        ''' % (scr, css)
        self.web_view.page().currentFrame().evaluateJavaScript(addresources)

        # Display processor warnings, if any
        if warn:
            QtWidgets.QMessageBox.warning(self, 'Processor message', warn)

    def after_update(self):
        '''Restore scroll position.'''

        # Restore scroll position
        try:
            pos = self.scroll_pos[self.filename]
        except KeyError:
            pass
        else:
            self.web_view.page().currentFrame().evaluateJavaScript('window.scrollTo(%s, %s);' % (pos.x(), pos.y()))

    @staticmethod
    def set_stylesheet(self, stylesheet='default.css'):
        path = os.path.join(stylesheet_dir, stylesheet)
        url = QtCore.QUrl.fromLocalFile(path)
        self.web_view.settings().setUserStyleSheetUrl(url)

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
            path = Settings.get('processor_path', 'pandoc')
            args = Settings.get('processor_args', '')
            args = ('%s' % (args)).split() + [self.filename]
            caller = QtCore.QProcess()
            caller.start(path, args)
            caller.waitForFinished()
            html = str(caller.readAllStandardOutput(), 'utf8')
            with io.open(filename, 'w', encoding='utf8') as f:
                f.writelines(str(html))
                f.close()
        else:
            pass

    def show_search_panel(self):
        self.addToolBar(0x8, self.search_bar)
        self.search_bar.show()
        self.field.setFocus()
        self.field.selectAll()

    def find(self, text, btn=''):
        p = self.web_view.page()
        back = p.FindFlags(1) if btn is self.prev else p.FindFlags(0)
        case = p.FindFlags(2) if self.case.isChecked() else p.FindFlags(0)
        wrap = p.FindFlags(4) if self.wrap.isChecked() else p.FindFlags(0)
        p.findText('', p.FindFlags(8))
        p.findText(text, back | wrap | case)

    def about(self):
        msg_about = QtWidgets.QMessageBox(0, 'About MDviewer', u'MDviewer\n\nVersion: %s' % (VERSION), parent=self)
        msg_about.show()

    def set_menus(self):

        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')

        for d in (
                {'label': u'&Open...',      'keys': 'Ctrl+O', 'func': self.open_file},
                {'label': u'&Save HTML...', 'keys': 'Ctrl+S', 'func': self.save_html},
                {'label': u'&Find...',      'keys': 'Ctrl+F', 'func': self.show_search_panel},
                {'label': u'&Print...',     'keys': 'Ctrl+P', 'func': self.print_doc},
                {'label': u'&Quit',         'keys': 'Ctrl+Q', 'func': self.quit}
                 ):
            action = QtWidgets.QAction(d['label'], self)
            action.setShortcut(d['keys'])
            action.triggered.connect(d['func'])
            file_menu.addAction(action)

        view_menu = menubar.addMenu("&View")

        for d in (
                {'label': u'Zoom &In',     'keys': 'Ctrl++', 'func': lambda: self.web_view.setZoomFactor(self.web_view.zoomFactor()+.1)},
                {'label': u'Zoom &Out',    'keys': 'Ctrl+-', 'func': lambda: self.web_view.setZoomFactor(self.web_view.zoomFactor()-.1)},
                {'label': u'&Actual Size', 'keys': 'Ctrl+=', 'func': lambda: self.web_view.setZoomFactor(1)}
                 ):
            action = QtWidgets.QAction(d['label'], self)
            action.setShortcut(d['keys'])
            action.triggered.connect(d['func'])
            view_menu.addAction(action)

        if os.path.exists(stylesheet_dir):
            default = ''
            sheets = []
            for f in os.listdir(stylesheet_dir):
                if not f.endswith('.css'): continue
                sheets.append(QtWidgets.QAction(f, self))
                if len(sheets) < 10:
                    sheets[-1].setShortcut('Ctrl+%d' % len(sheets))
                sheets[-1].triggered.connect(
                    lambda x, stylesheet=f: self.set_stylesheet(self, stylesheet))
            style_menu = menubar.addMenu('&Style')
            for item in sheets:
                style_menu.addAction(item)
            self.set_stylesheet(self, 'default.css')

        help_menu = menubar.addMenu("&Help")

        for d in (
                {'label': u'About...', 'func': self.about},
                 ):
            action = QtWidgets.QAction(d['label'], self)
            action.triggered.connect(d['func'])
            help_menu.addAction(action)

        # Define shortcuts
        self.scroll_down = QtWidgets.QShortcut("j", self, activated = lambda: self.web_view.page().currentFrame().scroll(0,+self.web_view.page().viewportSize().height()))
        self.scroll_up   = QtWidgets.QShortcut("k", self, activated = lambda: self.web_view.page().currentFrame().scroll(0,-self.web_view.page().viewportSize().height()))
        self.show_toc    = QtWidgets.QShortcut("t", self, activated = lambda: self.web_view.page().currentFrame().evaluateJavaScript('(function() {generateTOC();})()'))

        # Redefine context menu for reloading
        reload_action = self.web_view.page().action(QtWebKitWidgets.QWebPage.Reload)
        reload_action.setShortcut(QtGui.QKeySequence.Refresh)
        reload_action.triggered.connect(self.thread1.run)
        self.web_view.addAction(reload_action)

    def set_search_panel(self):
        self.search_bar = QtWidgets.QToolBar()

        # Define buttons
        self.done = QtWidgets.QPushButton(u'Done', self)
        self.case = QtWidgets.QPushButton(u'Case', self)
        self.wrap = QtWidgets.QPushButton(u'Wrap', self)
        self.next = QtWidgets.QPushButton(u'Next', self)
        self.prev = QtWidgets.QPushButton(u'Previous', self)

        # Define text field
        class DUMB(QtWidgets.QLineEdit): pass
        self.field = DUMB()

        # Restart search at button toggling
        def _toggle_btn(btn=''):
            self.field.setFocus()
            self.find(self.field.text(), btn)

        # Hide search panel
        def _escape():
            if self.search_bar.isVisible():
                self.search_bar.hide()

        # Add widgets to search panel
        for w in (self.done, self.case, self.wrap, self.field, self.next, self.prev):
            self.search_bar.addWidget(w)
            if type(w) == QtWidgets.QPushButton:
                w.setFlat(False)
                if any(t for t in (self.case, self.wrap) if t is w):
                    w.setCheckable(True)
                    w.clicked.connect(_toggle_btn)
                if any(t for t in (self.next, self.prev) if t is w):
                    w.pressed[()].connect(lambda btn=w: _toggle_btn(btn))
        self.done.pressed.connect(_escape)

        # Activate incremental search
        self.field.textChanged.connect(self.find)

    def print_doc(self):
        dialog = QtPrintSupport.QPrintPreviewDialog()
        dialog.paintRequested.connect(self.web_view.print_)
        dialog.exec_()

    def quit(self, QCloseEvent):

        # Save settings
        self.QSETTINGS.setValue('size', self.size())
        self.QSETTINGS.setValue('pos', self.pos())

        QtWidgets.qApp.quit()

class WatcherThread(QtCore.QThread):

    update = pyqtSignal(str, str)

    def __init__(self, filename):
        QtCore.QThread.__init__(self)
        self.filename = filename

    def run(self):
        warn = ''
        html, warn = self.processor_rules()
        self.update.emit(html, warn)

    def processor_rules(self):
        path = Settings.get('processor_path', 'pandoc')
        args = Settings.get('processor_args', '')
        args = ('%s' % (args)).split() + [self.filename]
        caller = QtCore.QProcess()
        caller.start(path, args)
        caller.waitForFinished()
        html = str(caller.readAllStandardOutput(), 'utf8')
        warn = str(caller.readAllStandardError(), 'utf8')
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

