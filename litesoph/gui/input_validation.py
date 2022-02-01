import tkinter as tk
from tkinter import ttk
from decimal import Decimal
from pathlib import Path

class Onlydigits(ttk.Entry):
    def __init__(self, parent, *args, **kwargs):
      super().__init__(parent, *args, **kwargs)
      self.configure(
        validate='all',
        validatecommand=(self.register(self.validate_digit), '%P'),
        )
    def validate_digit(self, input):
      if input.isdigit():
        return True 
      elif input is "":
        return True
      else:
        return False

class Onechar(ttk.Entry):
    def __init__(self, parent, *args, **kwargs):
      super().__init__(parent, *args, **kwargs)
      self.configure(
        validate='all',
        validatecommand=(self.register(self.validate_len), '%P'),
        )
    def validate_len(self, input):
      return len(input) <= 1

class Validatedconv(ttk.Entry):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.configure(
        validate='all',
        validatecommand=(self.register(self.validate), '%P'),
        )
  def validate(self, input, **kwargs):
    if any([(input not in '-1234567890e.')]):
      return False 
    elif input is "":
      return True
    else: 
      return False
 
class Decimalentry(ttk.Entry):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.configure(
        validate='all',
        validatecommand=(self.register(self.validate), '%P'),
        )
  def validate(self, inp):
    try:
        return True if float(inp) <= 10 else inp == ''
    except:
        return False

class FourChar(ttk.Entry):
    def __init__(self, parent, *args, **kwargs):
      super().__init__(parent, *args, **kwargs)
      self.configure(
        validate='all',
        validatecommand=(self.register(self._validate), '%P'),
        )
    def _validate(self, proposed):
      return len(proposed) <= 4


