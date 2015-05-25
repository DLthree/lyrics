import sys
import logging

logging.basicConfig()

from PyQt4 import QtGui, QtCore, QtScript
from PyQt4.QtScript import QScriptEngine, QScriptValue

class ScriptEngineRunError(Exception):
    pass

class ScriptEngine(QScriptEngine):
    def __init__(self, *args, **kwargs):
        app = QtCore.QCoreApplication.instance()
        if app is None:
            app = QtCore.QCoreApplication(sys.argv[:1])
        self.app = app
        super().__init__(*args, **kwargs)

    def import_extension(self, ext):
        res = self.importExtension(ext)
        if not res.isUndefined():
            raise Exception(res.toVariant()['message'])

    def add_function(self, name, fn):
        f = self.newFunction(fn)
        self.globalObject().setProperty(name, f)

    def check_error(self, res, filename=""):
        if res.isError():
            error = res.toVariant()
            filename = error['fileName'] or filename
            raise ScriptEngineRunError("%s:%d - %s" % (
                filename, error['lineNumber'], error['message']))
        return res

    def run(self, filename):
        res = self.evaluate(open(filename, "r").read())
        self.check_error(res, filename)
        return res.toVariant()

class LyricsEngine(ScriptEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for ext in ["qt.core", "qt.xml"]:
            self.import_extension(ext)
        self.run("lyrics.js")

    def get_lyrics(self, artist, song):
        res = self.evaluate('getLyrics("%s", "%s", "");' % (
            artist, song))
        self.check_error(res)
        return res.toVariant()
        
        
if __name__ == "__main__":
    se = LyricsEngine()
    print(se.get_lyrics("taylor swift", "love story"))
    # import pdb; pdb.set_trace() ## DEBUG ##
    
