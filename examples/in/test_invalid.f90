    implicit none
   private
     public :: dp, test_routine, &
                 test_function,  test_type,    str_function
   integer,   parameter :: dp = selected_real_kind ( 15 , 307)
   type  test_type
      real  (kind =dp ) :: r = 1.0d-3
      integer :: i
   end type test_type

contains


   subroutine test_routine( &
   r, i, j, k, l)
        integer, intent(in)                                :: r, i, j, k
       integer,   intent (out)                               :: l

    l  = test_function(r,i,j,k)

 pure function test_function(r, i, j, &
                                        k &
   result(l)
   integer, intent(in)                                :: r, i, j, k
   integer                                            :: l

      l=r + i +j  +k
   end function
   function &
        str_function(a)      result(l)
      character(len=*)                                   :: a
      integer                                            :: l

     if(len(a)<5)then
       l=0
      else
       l=1
end function

end module

program example_prog
 use example, only: dp, test_routine, test_function, test_type,str_function

   implicit  none
  integer :: r,i,j,k,l,my_integer,m
     integer, dimension(5) :: arr
   integer, dimension(20) :: big_arr
integer :: endif
   type(test_type) :: t
real(kind=dp) :: r1,   r2,  r3, r4, r5,  r6
  integer, pointer :: point

  point=>  null( )

   r1=-(r2**i*r3+r5*(-r4 &
   - 3)-r6))-2.e+2
   r1=-(r2**i*r3+(r5*(-r4 &
   - 3)-r6-2.e+2
   if( r.eq.2.and.r<=5) i=3
   write(*, *)(&
   merge(3, 1, i<=2)
   write(*, *) test_function(r,i,j , k)
END MODULE
ENDPROGRAM
ENDIF
ENDDO
FUNCTION a(b)
   integer :: a
   ENDFUNCTION
   END SUBROUTINE

