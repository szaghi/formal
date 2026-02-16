module sample_physics
!< A sample physics module for testing.
!< Supports 1D and 2D.

use iso_fortran_env, only: real64

implicit none

real(real64), parameter :: PI = 3.14159265358979_real64 !< Pi constant.

type :: config_type
   !< Configuration container.
   integer :: order = 5  !< Scheme order.
   real(real64) :: cfl = 0.8_real64 !< CFL number.
   contains
      procedure :: init !< Initialize configuration.
end type config_type

contains

subroutine init(self, order, cfl)
!< Initialize the configuration.
class(config_type), intent(inout) :: self  !< Config object.
integer, intent(in) :: order               !< Scheme order.
real(real64), intent(in) :: cfl            !< CFL number.
self%order = order
self%cfl = cfl
end subroutine init

function compute_dt(cfl, dx, velocity) result(dt)
!< Compute time step from CFL condition.
!< $$ \Delta t = \text{CFL} \cdot \frac{\Delta x}{|v|} $$
real(real64), intent(in) :: cfl      !< CFL number.
real(real64), intent(in) :: dx       !< Grid spacing.
real(real64), intent(in) :: velocity !< Flow velocity.
real(real64) :: dt                   !< Time step.
dt = cfl * dx / abs(velocity)
end function compute_dt

end module sample_physics
