fprettify
=========

|License: GPL v3|

fprettify is an auto-formatter for modern Fortran code that imposes
strict whitespace formatting.

Features
--------

-  Auto-indentation.
-  Line continuations are aligned with the previous opening delimiter
   ``(``, ``[`` or ``(/`` or with an assignment operator ``=`` or
   ``=>``. If none of the above is present, a default hanging indent is
   applied.
-  Consistent amount of whitespace around operators and delimiters.
-  Removal of extraneous whitespace and consecutive blank lines.
-  Works only for modern Fortran (Fortran 90 upwards).
-  Tested for editor integration.
-  By default, fprettify causes changes in the amount of whitespace only
   and thus preserves revision history.

Example
--------

.. code:: fortran

    program demo
    integer :: endif,if,else
    endif=3; if=2
    if(endif==2)then
    endif=5
    else=if+4*(endif+&
    2**10)
    else if(endif==3)then
    print*,endif
    endif
    end program

⇩⇩⇩⇩⇩⇩⇩⇩⇩⇩ ``fprettify`` ⇩⇩⇩⇩⇩⇩⇩⇩⇩⇩

.. code:: fortran

    program demo
       integer :: endif, if, else
       endif = 3; if = 2
       if (endif == 2) then
          endif = 5
          else = if + 4*(endif + &
                         2**10)
       else if (endif == 3) then
          print *, endif
       endif
    end program

Usage
-----

Autoformat file1, file2, ... inplace by

::

    fprettify file1, file2, ...

The default indent is 3. If you prefer something else, use
``--indent n`` argument. For more options, read

::

    fprettify -h

For editor integration, use

::

    fprettify --silent

For instance, with Vim, use fprettify with ``gq`` by putting the
following commands in your ``.vimrc``:

.. code:: vim

    autocmd Filetype fortran setlocal formatprg=fprettify\ --silent

.. |License: GPL v3| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
   :target: http://www.gnu.org/licenses/gpl-3.0
