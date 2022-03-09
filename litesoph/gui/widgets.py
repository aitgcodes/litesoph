import tkinter as tk
import csv
from tkinter import ttk
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


class LabelInput(tk.Frame):
  """A widget containing a label and input together."""
  def __init__(
    self, parent, label, var, input_class=ttk.Entry,
    input_args=None, label_args=None, **kwargs
  ):
    super().__init__(parent, **kwargs)
    input_args = input_args or {}
    label_args = label_args or {}
    self.variable = var
    self.variable.label_widget = self

    #to set the text argument of the widget
    if input_class in (ttk.Checkbutton, ttk.Button):
      input_args["text"] = label
    else:
      self.label = ttk.Label(self, text=label, **label_args)
      self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

    #to set up the input arguments so that the input's control variable willbe passed
    if input_class in (
      ttk.Checkbutton, ttk.Button, ttk.Radiobutton, ValidatedRadioGroup
    ):
      input_args["variable"] = self.variable
    else:
      input_args["textvariable"] = self.variable
    
    #in the case of a radiobutton  
    if input_class == ttk.Radiobutton:
      self.input = tk.Frame(self)
      for v in input_args.pop('values', []):
        button = ttk.Radiobutton(
          self.input, value=v, text=v, **input_args
        )
        button.pack(
          side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x'
        )
    #in the case of a nonradiobutton
    else:
      self.input = input_class(self, **input_args)
      self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
      self.columnconfigure(0, weight=1)

  def grid(self, sticky=(tk.E + tk.W), **kwargs):
    """Override grid to add default sticky values"""
    super().grid(sticky=sticky, **kwargs)

