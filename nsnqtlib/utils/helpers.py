# -*- coding: utf-8 -*-
import os
import platform

_platform = platform.system().lower()

is_osx = (_platform == 'darwin')
is_win = (_platform == 'windows')
is_lin = (_platform == 'linux')
