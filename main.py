#coding: utf-8

from pyside_loadui import loadUi
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QGridLayout, QLineEdit, QPushButton, QApplication, QMainWindow, QActionGroup, QAction, QFileDialog, QMessageBox
from PySide2.QtGui import QIcon
import sys
import os
import math
import qdarkstyle
import qdarkgraystyle
# import utils
from utils import PS1, USAGE, CodeBlock, is_expression
from dataclasses import dataclass
from io import StringIO
from typing import Iterator
import pandas as pd
import numpy as np
import yaml
from collections import Counter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = None

# define some global variables for the application,
# and the global variables will used in the eval/exec function
ALL = A = B = C = D = E = F = G = H = I = J = K = L = None
modelIndex = 0
data = None
global_symbols = globals()


def load_configuration():
    '''Load the configuration file and return the data as dict'''
    global data
    with open('configuration.yaml', encoding='utf-8') as f:
        data = yaml.safe_load(f)


def execute_setup_code():
    global data
    # execute the setup code, provide some utilities like parseData
    exec(data['setupCode'], global_symbols)


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        loadUi('main.ui', self)
        self.setWindowIcon(QIcon('icon.png'))

        actionGroupDefaultStyle = QActionGroup(self)
        actionGroupDefaultStyle.addAction(self.actionFusion)
        actionGroupDefaultStyle.addAction(self.actionWindows)
        actionGroupDefaultStyle.addAction(self.actionWindowsVista)
        actionGroupDefaultStyle.setExclusive(True)

        actionGroupStyle = QActionGroup(self)
        actionGroupStyle.addAction(self.actionQdarkstyle)
        actionGroupStyle.addAction(self.actionQdarkgraystyle)
        actionGroupStyle.addAction(self.actionMyStyle)
        actionGroupStyle.addAction(self.actionResetStyle)
        actionGroupStyle.setExclusive(True)
        self.show()

    @Slot()
    def on_action_triggered(self):
        action = self.sender()
        text = action.text()
        if text == "Exit":
            app.quit()
        elif text == "Open":
            # open the data file specified by the user and put it in the textEditData
            filePath, _ = QFileDialog.getOpenFileName(
                self, caption='打开数据文本文件', filter='Text Files (*.txt)')
            logger.info(f'filePath:{filePath}, _:{_}')
            if filePath:
                f = open(filePath, 'r', encoding='utf-8')
                with f:
                    data = f.read()
                    # shirnk the input data, replace the tab to one space
                    data = data.replace('\t', ' ')
                    self.textEditData.setText(data)
                QMessageBox.information(self, "提示", "已加载数据文本文件内容到输入数据区")
        elif text == "Save":
            if self.textEditResult.toPlainText() == "":
                return QMessageBox.warning(self, '警告', '结果区为空，请先计算结果')
            # open the result file specified by the user for saving textEditResult content
            filePath, _ = QFileDialog.getSaveFileName(
                self, caption='打开结果保存文件', filter='Text Files (*.txt)')
            logger.info(f'filePath:{filePath}, _:{_}')
            if filePath:
                f = open(filePath, 'w', encoding='utf-8')
                with f:
                    data = f.write(self.textEditResult.toPlainText())
                QMessageBox.information(self, "提示", "保存成功")

        elif text == "Fusion":
            app.setStyle('Fusion')
        elif text == "Windows":
            app.setStyle('Windows')
        elif text == "WindowsVista":
            app.setStyle('WindowsVista')
        elif text == "Qdarkstyle":
            # https://github.com/ColinDuquesnoy/QDarkStyleSheet
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        elif text == "Qdarkgraystyle":
            # https://github.com/mstuttgart/qdarkgraystyle
            self.setStyleSheet(qdarkgraystyle.load_stylesheet())
        elif text == "MyStyle":
            self.setStyleSheet(open('style/material/material-blue.qss').read())
        elif text == "ResetStyle":
            self.setStyleSheet("")

    @Slot()
    def on_line_edit_return_pressed(self):
        expression = self.lineEditInput.text().strip()
        self.textEditConsole.append(f"{PS1}{expression}")
        # Handle special commands
        if expression.lower() == "help":
            self.textEditConsole.append(USAGE)
        elif expression.lower() == "clear":
            return self.textEditConsole.setText(f"{PS1}")
        # Evaluate the expression and handle errors
        try:
            if is_expression(expression):
                logger.info(f"Evaluating expression: {expression}")
                # execute the expression
                try:
                    result = eval(expression, global_symbols)
                    # print the result
                    self.textEditConsole.append(f"{result}")
                except Exception as e:
                    logger.error(f"Error: {e}")
                    self.textEditConsole.append(f"Error: {e}")
            else:
                logger.info(f"Execute statement: {expression}")
                try:
                    exec(expression, global_symbols)
                    self.textEditConsole.append(f"Executed statement!")
                except Exception as e:
                    logger.error(f"Error: {e}")
                    self.textEditConsole.append(f"Error: {e}")
        except SyntaxError:
            # If the user enters an invalid expression
            self.textEditConsole.append("Invalid input expression syntax")
        except (NameError, ValueError) as err:
            # If the user tries to use a name that isn't allowed
            # or an invalid value for a given math function
            self.textEditConsole.append(str(err))
        # TextEdit scroll to the bottom
        self.textEditConsole.ensureCursorVisible()
        # self.textEditConsole.setFocus()
        
        
    @Slot()
    def on_combobox_activated(self):
        global modelIndex
        text = self.comboBoxCalculateModel.currentText()
        modelIndex = self.comboBoxCalculateModel.currentIndex()
        self.textEditData.setText("")
        self.initializeData()
        

    @Slot()
    def on_button_clicked(self):
        button = self.sender()
        if button == self.pushButtonStatistics:
            # clear the result text edit
            self.textEditResult.clear()
            # load the data in case it's changed again
            self.initializeData()
            codeblocks = [CodeBlock(**codeblock)
                          for codeblock in data[f'OperationCodeBlocks{modelIndex + 1}']]
            for index, codeblock in enumerate(codeblocks, start=1):
                try:
                    exec(codeblock.code, global_symbols)
                    value = ' '.join(
                        [f"{item:02}" for item in sorted(globals()[codeblock.name])])
                    self.textEditResult.append(
                        f'{index:02d}: {codeblock.description}: {value}\n')
                except Exception as e:
                    logger.error(f"Error: {e}")
                    self.textEditResult.append(
                        f'{index:02d}: {codeblock.description}: Error: {e}\n')

  
    def initializeWidget(self):
        self.comboBoxCalculateModel.addItems(['基础测算工具','基固工具','竹园工具'])
        self.comboBoxCalculateModel.setCurrentIndex(0)


    def initializeData(self):
        global data, ALL, A, B, C, D, E, F, G, H, I, J, K, L
        if self.textEditData.toPlainText() == "":
            # get the sample data
            inputData = data[f'sampleData{modelIndex + 1}']
            # shirnk the input data, replace the tab to one space
            inputData = inputData.replace('\t', ' ')
            self.textEditData.setText(inputData)
        # parse the sample data
        if modelIndex == 0:
            ALL, A, B, C, D = globals()[f'parseData{modelIndex + 1}'](self.textEditData.toPlainText())
        elif modelIndex == 1:
            ALL, A, B, C, D = globals()[f'parseData{modelIndex + 1}'](self.textEditData.toPlainText())
        elif modelIndex == 2:
            ALL, A, B, C, D, E, F, G, H, I, J, K, L = globals()[f'parseData{modelIndex + 1}'](self.textEditData.toPlainText())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_configuration()
    execute_setup_code()
    window = Window()
    window.initializeWidget()
    window.initializeData()
    sys.exit(app.exec_())
