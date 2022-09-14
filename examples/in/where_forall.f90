! Forall-construct

! Example 1

forall(I = 3:N + 1, J = 3:N + 1)
  C(I, J) = C(I, J + 2) + C(I, J - 2) + C(I + 2, J) + C(I - 2, J)
  D(I, J) = C(I, J)
end forall

! Example 2

forall(I = 3:N + 1, J = 3:N + 1)
C(I, J) = C(I, J + 2) + C(I, J - 2) + C(I + 2, J) + C(I - 2, J)
D(I, J) = C(I, J)
end forall

! Example 3

forall(I = 3:N + 1, J = 3:N + 1)
  C(I, J) = C(I, J + 2) + C(I, J - 2) + C(I + 2, J) + C(I - 2, J)
  D(I, J) = C(I, J)
    end forall

! Where-construct

! Example 1

where (C/=0)
    A=B/C
elsewhere
    A=0.0
end where

! Example 2

where (C/=0)
A=B/C
elsewhere
A=0.0
end where

! Example 3

where (C/=0)
    A=B/C
     elsewhere
  A=0.0
    end where
