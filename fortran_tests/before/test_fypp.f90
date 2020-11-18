#:if DEBUG > 0
print *, "Some debug information"
#:endif

#:set LOGLEVEL = 2
print *, "LOGLEVEL: ${LOGLEVEL}$"

#:del LOGLEVEL

#:def assertTrue(cond)
#:if DEBUG > 0
 if  (.not.    ${cond}$ )   then
  print*,"Assert failed in file ${_FILE_}$, line ${_LINE_}$"
   error  stop
 end if
#:endif
#:enddef assertTrue

! Invoked via direct call (argument needs no quotation)
@:assertTrue(size(myArray) > 0)

! Invoked as Python expression (argument needs quotation)
$:assertTrue('size(myArray) > 0')

program test
#:if defined('WITH_MPI')
  use   mpi
#:elif defined('WITH_OPENMP')
    use openmp
#:else
use serial
#:endif
  end program

interface myfunc
#:for dtype in ['real', 'dreal', 'complex', 'dcomplex']
  module procedure   myfunc_${dtype}$
#:endfor
 end interface myfunc

logical,parameter :: hasMpi = #{if  defined('MPI')}# .true. #{else}# .false. #{endif}#

character(*), parameter :: comp_date   ="${time.strftime('%Y-%m-%d')}$"

#:include "macrodefs.fypp"

#:if var1  > var2 &
    & or  var2>   var4
  print *,"Doing something here"
#:endif

#! Callable needs only string argument
#:def debug_code(code)
  #:if DEBUG > 0
    $:code
  #:endif
#:enddef debug_code

#! Pass code block as first positional argument
#:call debug_code
  if  (size(array) >   100) then
  print *,"DEBUG: spuriously large array"
end if
#:endcall debug_code

#! Callable needs also non-string argument types
#:def repeat_code(code, repeat)
  #:for ind in range(repeat)
    $:code
  #:endfor
#:enddef repeat_code

#! Pass code block as positional argument and 3 as keyword argument "repeat"
#:call repeat_code(repeat=3)
this will be repeated 3 times
#:endcall repeat_code

#! This will not show up in the output
#! Also the newline characters at the end of the lines will be suppressed

#! Definitions are read, but no output (e.g. newlines) will be produced
#:mute
#:include "macrodefs.fypp"
#:endmute

#:if DEBUGLEVEL < 0
  #:stop 'Negative debug level not allowed!'
#:endif

#:def mymacro(RANK)
  #! Macro only works for RANK 1 and above
  #:assert RANK > 0
#:enddef mymacro

program test
#:if defined('MPI')
use mpi
#:endif
end program

#{if 1 > 2}#Some code#{endif}#

@:mymacro(a<b)

print *, @{mymacro(a <b)}@

#:if defined('DEBUG')  #! The Python function defined() expects a string argument
#:for dtype in ['real(dp)', 'integer', 'logical']  #! dtype runs over strings

print *, "This is line nr. ${_LINE_}$ in file '${_FILE_}$'"

print *, "Rendering started ${_DATE_}$ ${_TIME_}$"

$:setvar('i', 1, 'j', 2)
print *, "VAR I: ${i}$, VAR J: ${j}$"

$:delvar('i', 'j')

#{set X = 2}#print *, ${X}$

#:set real_kinds = ['sp', 'dp']

interface sin2
#:for rkind in real_kinds
  module procedure sin2_${rkind}$
#:endfor
end interface sin2

#:for rkind in real_kinds
function sin2_${rkind}$(xx) result(res)
  real(${rkind}$), intent(in) :: xx
  real(${rkind}$) :: res

  res=sin(xx) * sin(xx)

end function sin2_${rkind}$
#:endfor

#:set kinds = ['sp', 'dp']
#:set names = ['real', 'dreal']
#! create kinds_names as [('sp', 'real'), ('dp', 'dreal')]
#:set kinds_names = list(zip(kinds, names))

#! Acces by indexing
interface sin2
#:for kind_name in kinds_names
  module procedure sin2_${kind_name[1]}$
#:endfor
end interface sin2

#! Unpacking in the loop header
#:for kind, name in kinds_names
function sin2_${name}$(xx) result(res)
  real(${kind}$),   intent(in) :: xx
   real(${kind}$) :: res

 res =   sin(xx) * sin(xx)

end function sin2_${name}$
#:endfor

#:def assertTrue(cond)
#:if DEBUG > 0
if (.not. (${cond}$)) then
  print *,"Assert failed!"
  error stop
end if
#:endif
#:enddef

#:def macro(X, *VARARGS)
X=${X}$, VARARGS=#{for ARG in VARARGS}#${ARG}$#{endfor}#
#:enddef macro

$:macro(1,2, 3)   #! Returns "X=1, VARARGS=23"

! Rather ugly
print *, #{call choose_code}# a(:) #{nextarg}# size(a) #{endcall}#

! This form is more readable
print *, ${choose_code('a(:)', 'size(a)')}$

! Alternatively, you may use a direct call (see next section)
print *, @{choose_code(a(:), size(a))}@

@:assertEqual(size(coords, dim=2), &
    & size( atomtypes))

#! Using choose_code() macro defined in previous section
  print *, @{choose_code(a(:),size(a))}@

#:if a >  b &
    & or b > c &
    & or c>d
$:somePythonFunction(  param1, &
    &param2)

#:mute

#! Enable debug feature if the preprocessor variable DEBUG has been defined
#:set DEBUG = defined('DEBUG')


#! Stops the code, if the condition passed to it is not fulfilled
#! Only included in debug mode.
#:def ensure(cond, msg=None)
  #:if DEBUG
    if (.not.  (${cond}$)) then
      write(*,*) 'Run-time check failed'
      write(*,*)  'Condition: ${cond.replace("'", "''")}$'
      #:if msg is not None
        write(*,*)  'Message: ', ${msg}$
      #:endif
      write(*,*)'File: ${_FILE_}$'
      write(*,*) 'Line: ', ${_LINE_}$
      stop
    end if
  #:endif
#:enddef ensure


#! Includes code if in debug mode.
#:def debug_code(code)
  #:if DEBUG
$:code
  #:endif
#:enddef debug_code

#:endmute

#:include 'checks.fypp'

module testmod
  implicit none

contains

  subroutine someFunction(ind, uplo)
    integer, intent(in) :: ind
   character, intent(in) :: uplo

     @:ensure(ind > 0, msg="Index must be positive")
    @:ensure(uplo == 'U' .or. uplo == 'L')

    ! Do something useful here

  #:call debug_code
     print *, 'We are in debug mode'
    print *, 'The value of ind is', ind
  #:endcall debug_code

  end subroutine someFunction

end module testmod


#:def ranksuffix(RANK)
$:'' if RANK == 0 else '(' + ':' + ',:' * (RANK - 1) + ')'
#:enddef ranksuffix

#:set PRECISIONS = ['sp', 'dp']
#:set RANKS = range(0, 8)

module errorcalc
  implicit none

  integer, parameter :: sp = kind(1.0)
  integer, parameter :: dp = kind(1.0d0)

  interface maxRelError
  #:for PREC in PRECISIONS
    #:for RANK in RANKS
      module procedure maxRelError_${RANK}$_${PREC}$
    #:endfor
  #:endfor
  end interface maxRelError

contains

#:for PREC in PRECISIONS
  #:for RANK in RANKS

  function maxRelError_${RANK}$_${PREC}$(obtained, reference) result(res)
    real(${PREC}$), intent(in) :: obtained${ranksuffix(RANK)}$
    real(${PREC}$), intent(in) :: reference${ranksuffix(RANK)}$
    real(${PREC}$) :: res

  #:if RANK == 0
    res = abs((obtained - reference) / reference)
  #:else
    res = maxval(abs((obtained - reference) / reference))
  #:endif

  end function maxRelError_${RANK}$_${PREC}$

  #:endfor
#:endfor

end module errorcalc

#:def maxRelError_template(RANK, PREC)
  function maxRelError_${RANK}$_${PREC}$(obtained, reference) result(res)
    real(${PREC}$), intent(in) :: obtained${ranksuffix(RANK)}$
    real(${PREC}$), intent(in) :: reference${ranksuffix(RANK)}$
    real(${PREC}$) :: res

  #:if RANK == 0
    res = abs((obtained - reference) / reference)
  #:else
    res = maxval(abs((obtained - reference) / reference))
  #:endif

  end function maxRelError_${RANK}$_${PREC}$
#:enddef maxRelError_template

#:for PREC in PRECISIONS
  #:for RANK in RANKS
    $:maxRelError_template(RANK, PREC)
  #:endfor
#:endfor

end module errorcalc

! tests for fypp directives inside Fortran continuation lines
call test(arg1,&
   ${a if a  > b else b}$, arg3, &
 #:if c>d
   c,&
 #:else
   d,&
 #:endif
   arg4)
