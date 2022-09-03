# statistics_app

### How to run

1. pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
2. python main.py # for gui version
3. python utils.py # for gui version


### How to package

If `packenv` is not exists, use the following commands to create it.

- `python -m venv packenv` # create the packenv
- `packenv\scripts\activate.bat` # activate the packenv
- `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple` # install the requirements

- `packenv\scripts\activate.bat` # activate the packenv
- `pyinstaller main.py --name statistics_app --add-data main.ui;./ --add-data configuration.yaml;./ --add-data sample.txt;./ --add-data style;style --icon icon.ico --windowed --noconfirm --hidden-import qdarkstyle --hidden-import qdarkgraystyle` # if the pyistaller spec file does not exists
- `pyinstaller statistics_app.spec` # if the pyistaller spec file exists

### Some other staff

Other package utiles

[nuitka](https://github.com/Nuitka/Nuitka)

`nuitka --standalone --show-memory --show-progress --nofollow-imports --plugin-enable=pyqt5 --follow-import-to=utils --output-dir=out --windows-icon-from-ico=./icon.ico main.py`

[pyoxidizer](https://github.com/indygreg/PyOxidizer/issues/610)

`pyoxidizer run`

### Some reference

- https://realpython.com/python-eval-function/#using-pythons-eval-with-input
- https://realpython.com/python-yaml/
- https://realpython.com/run-python-scripts/
- https://yaml-multiline.info/
- https://pythonpyqt.com/pyqt-qtextedit/
- https://coderslegacy.com/python/pyqt5-qtextedit/
- https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QTextEdit.html#PySide2.QtWidgets.PySide2.QtWidgets.QTextEdit.toPlainText
- https://blog.csdn.net/wowocpp/article/details/103396348
- https://blog.csdn.net/qyj980825/article/details/122287371
- https://blog.csdn.net/qq_34414530/article/details/108172038
- https://www.cnblogs.com/XJT2018/p/10208710.html
- https://appdividend.com/2022/06/24/python-ordered-set/
- https://www.askpython.com/python/remove-duplicate-elements-from-list-python
- https://realpython.com/pyinstaller-python/#customizing-your-builds
- https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/
- https://newbedev.com/no-module-named-when-using-pyinstaller
- https://github.com/liudonghua123/pyqt5-calculator
- https://gregoryszorc.com/docs/pyoxidizer/main/pyoxidizer_getting_started.html
- https://github.com/giftmischer69/easy_oxidize


