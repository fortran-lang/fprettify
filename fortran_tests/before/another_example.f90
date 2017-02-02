module a_mod
integer :: a_variable, another_variable

  private :: a_variable, &
                   another_variable
   contains

   subroutine test_type(bohoo)
   class(*), intent(in) :: bohoo

     select type(bohoo)
     type is(real)
     write(*,*) 'T'
    type is(integer)
       write(*,*) 'F'
    class default
   end select

    return

      end subroutine test_type

   end module a_mod

program test
   use a_mod

      integer :: block_test=2, block =    2
   real :: res, factor    = 2.81

namelist/test_nml/block, block_test, res, factor

      block = 5

         block
            real :: another_real
            another_real = 4.5
            end block

   call test_type(block)

            block ! have more vars
       real :: block
          call test_type(block)
                              end block

                              block = block*5/block_test+1
     ! whitespace 2
!  res = factor*5/block_test + 1
   res = factor*5/block_test + 1
    ! whitespace 3
!  res = factor * 5 / block_test + 1
      res = factor * 5 / block_test + 1

         stop

      end program test
