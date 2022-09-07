import logging
from collections import Counter
from dataclasses import dataclass
from io import StringIO
from typing import Iterator

import flet
import numpy as np
import pandas as pd
import yaml
from flet import *
from flet import dropdown, icons

from utils import PS1, USAGE, CodeBlock, is_expression

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

common_height = 35
common_text_size = 12

# define some global variables for the application,
# and the global variables will used in the eval/exec function
ALL = A = B = C = D = E = F = G = H = I = J = K = L = None
data = None
global_symbols = globals()

about_markdown_content = None
# read readme.md for about content
with open("readme.md", "r") as f:
  about_markdown_content = f.read()


def load_configuration():
  """Load the configuration file and return the data as dict"""
  global data
  with open("configuration.yaml", encoding="utf-8") as f:
    data = yaml.safe_load(f)


def execute_setup_code():
  global data
  # execute the setup code, provide some utilities like parseData
  exec(data["setupCode"], global_symbols)


def main(page: Page):
  app_name = "statistics_app"
  page.title = app_name

  # some refs
  model_dropdown = Ref[Dropdown]()
  command_textfield = Ref[TextField]()
  command_shell_textfield = Ref[TextField]()
  input_textfield = Ref[TextField]()
  result_textfield = Ref[TextField]()
  theme_switch = Ref[Switch]()

  # https://flet.dev/blog/using-custom-fonts-in-flet-app/
  # page.fonts = {
  #   "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",
  #   "Aleo Bold Italic": "https://raw.githubusercontent.com/google/fonts/master/ofl/aleo/Aleo-BoldItalic.ttf"
  # }

  default_theme = Theme(
    color_scheme_seed="purple",
    font_family="Microsoft YaHei UI",
  )
  page.theme = default_theme
  page.dark_theme = default_theme
  page.theme_mode = "light"

  # appbar
  page.appbar = AppBar(
    title=Text(app_name),
    center_title=False,
    actions=[
      Switch(
        ref=theme_switch,
        label="Light theme",
        tooltip="change the theme to light or dark",
        on_change=lambda e: theme_changed(e),
      ),
      IconButton(
        icons.FILE_OPEN,
        tooltip="open input file",
        on_click=lambda _: pick_files_dialog.pick_files(allowed_extensions=["txt"]),
      ),
      IconButton(
        icons.SAVE,
        tooltip="save result file",
        on_click=lambda _: save_files_dialog.save_file(allowed_extensions=["txt"]),
      ),
      # IconButton(icons.EXIT_TO_APP, on_click=lambda _: page.window_close()),
      PopupMenuButton(
        items=[
          PopupMenuItem(
            text="About",
            icon=icons.INFO,
            on_click=lambda e: open_about_dialog(e),
          ),
        ]
      ),
    ],
  )

  def initialize_data():
    global data, ALL, A, B, C, D, E, F, G, H, I, J, K, L
    modelIndex = int(model_dropdown.current.value)
    if input_textfield.current.value == "":
      # get the sample data
      inputData = data[f"sampleData{modelIndex + 1}"]
      # shirnk the input data, replace the tab to one space
      inputData = inputData.replace("\t", " ")
      input_textfield.current.value = inputData
    # parse the sample data
    if modelIndex == 0:
      ALL, A, B, C, D = globals()[f"parseData{modelIndex + 1}"](input_textfield.current.value)
    elif modelIndex == 1:
      ALL, A, B, C, D = globals()[f"parseData{modelIndex + 1}"](input_textfield.current.value)
    elif modelIndex == 2:
      ALL, A, B, C, D, E, F, G, H, I, J, K, L = globals()[f"parseData{modelIndex + 1}"](input_textfield.current.value)
    page.update()

  def model_change(e):
    modelIndex = int(model_dropdown.current.value)
    input_textfield.current.value = ""
    initialize_data()

  def calculate_button_click(e):
    # clear the result text edit
    result_textfield.current.value = ""
    # load the data in case it's changed again
    initialize_data()
    codeblocks = [CodeBlock(**codeblock) for codeblock in data[f"OperationCodeBlocks{int(model_dropdown.current.value) + 1}"]]
    for index, codeblock in enumerate(codeblocks, start=1):
      try:
        exec(codeblock.code, global_symbols)
        value = " ".join([f"{item:02}" for item in sorted(globals()[codeblock.name])])
        result_textfield.current.value = result_textfield.current.value + f"{index:02d}: {codeblock.description}: {value}\n"
      except Exception as e:
        logger.error(f"Error: {e}")
        result_textfield.current.value = result_textfield.current.value + f"{index:02d}: {codeblock.description}: Error: {e}\n"
    page.update()

  def command_submit(e):
    if command_shell_textfield.current.value == "":
      command_shell_textfield.current.value = f"{command_shell_textfield.current.value}{PS1}"
    expression = command_textfield.current.value.strip()
    command_shell_textfield.current.value = command_shell_textfield.current.value + f"{expression}\n"
    # Handle special commands
    if expression.lower() == "help":
      command_shell_textfield.current.value = command_shell_textfield.current.value + USAGE
    elif expression.lower() == "clear":
      command_shell_textfield.current.value = f"{PS1}"
      return None
    # Evaluate the expression and handle errors
    try:
      if is_expression(expression):
        logger.info(f"Evaluating expression: {expression}")
        # execute the expression
        try:
          result = eval(expression, global_symbols)
          # print the result
          command_shell_textfield.current.value = f"{command_shell_textfield.current.value}{result}\n"
        except Exception as e:
          logger.error(f"Error: {e}")
          command_shell_textfield.current.value = f"{command_shell_textfield.current.value}Error: {e}\n"
      else:
        logger.info(f"Execute statement: {expression}")
        try:
          exec(expression, global_symbols)
          command_shell_textfield.current.value = f"{command_shell_textfield.current.value}Executed statement!\n"
        except Exception as e:
          logger.error(f"Error: {e}")
          command_shell_textfield.current.value = f"{command_shell_textfield.current.value}Error: {e}\n"
    except SyntaxError:
      # If the user enters an invalid expression
      command_shell_textfield.current.value = f"{command_shell_textfield.current.value}Invalid input expression syntax\n"
    except (NameError, ValueError) as err:
      # If the user tries to use a name that isn't allowed
      # or an invalid value for a given math function
      command_shell_textfield.current.value = f"{command_shell_textfield.current.value}{str(err)}\n"

    command_shell_textfield.current.value = f"{command_shell_textfield.current.value}{PS1}"
    page.update()

  def theme_changed(e):
    page.theme_mode = "dark" if page.theme_mode == "light" else "light"
    theme_switch.current.label = "Light theme" if page.theme_mode == "light" else "Dark theme"
    page.update()

  page.add(
    Row(
      [
        Column(
          [
            TextField(
              ref=input_textfield,
              min_lines=100,
              label="Data:",
              expand=True,
              multiline=True,
              autofocus=True,
              text_size=common_text_size,
            ),
            Row(
              [
                Dropdown(
                  ref=model_dropdown,
                  label="model",
                  hint_text="Choose the model of calculation?",
                  content_padding=5,
                  text_size=common_text_size,
                  height=common_height,
                  options=[
                    dropdown.Option(key=0, text="基础测算工具"),
                    dropdown.Option(key=1, text="基固工具"),
                    dropdown.Option(key=2, text="竹园工具"),
                  ],
                  value=0,
                  expand=True,
                  on_change=model_change,
                ),
                FilledButton(
                  text="Calculate",
                  height=common_height,
                  icon=icons.CALCULATE,
                  on_click=calculate_button_click,
                ),
              ]
            ),
            TextField(
              ref=command_textfield,
              label="Enter command here...",
              height=common_height,
              text_size=common_text_size,
              on_submit=command_submit,
            ),
            TextField(
              ref=command_shell_textfield,
              label="Console",
              text_size=common_text_size,
              read_only=True,
              min_lines=100,
              expand=True,
              multiline=True,
            ),
          ],
          expand=True,
        ),
        Container(
          TextField(
            ref=result_textfield,
            read_only=True,
            text_size=common_text_size,
            height=10000,
            min_lines=500,
            label="Result:",
            expand=True,
            multiline=True,
          ),
          expand=True,
        ),
      ],
      expand=True,
      alignment="start",
    )
  )

  def pick_files_handle(e: FilePickerResultEvent):
    logger.info(f"e.files: {e.files}")
    if e.files:
      filePath = e.files[0]
      logger.info(f"open {filePath} input file")
      f = open(filePath.path, "r", encoding="utf-8")
      with f:
        data = f.read()
        # shirnk the input data, replace the tab to one space
        data = data.replace("\t", " ")
        input_textfield.current.value = data
      page.snack_bar = SnackBar(Text(f"已加载数据文本文件内容到输入数据区"))
      page.snack_bar.open = True
      page.update()

  def save_files_handle(e: FilePickerResultEvent):
    if e.control.result.path:
      filePath = e.control.result.path
      logger.info(f"save {filePath} result file")
      f = open(filePath, "w", encoding="utf-8")
      with f:
        data = f.write(result_textfield.current.value)
      page.snack_bar = SnackBar(Text(f"保存成功"))
      page.snack_bar.open = True
      page.update()

  def open_about_dialog(e):
    about_dialog.open = True
    page.update()

  pick_files_dialog = FilePicker(on_result=pick_files_handle)
  save_files_dialog = FilePicker(on_result=save_files_handle)
  about_dialog = AlertDialog(
    title=Text("About"),
    content=Markdown(
      about_markdown_content,
      width=600,
      selectable=True,
      extension_set="gitHubWeb",
      on_tap_link=lambda e: page.launch_url(e.data),
    ),
  )
  page.overlay.append(pick_files_dialog)
  page.overlay.append(save_files_dialog)
  page.overlay.append(about_dialog)

  load_configuration()
  execute_setup_code()
  initialize_data()
  
  page.update()


flet.app(
  target=main,
  # view=flet.WEB_BROWSER,
  # web_renderer="html"
)
