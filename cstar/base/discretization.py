import textwrap


class Discretization:
    """Holds discretization information about a Component."""

    time_step: int
    """The time step with which to run the Component"""
    n_procs_x: int
    """The number of parallel processors over which to subdivide the x axis of the domain."""
    n_procs_y: int
    """The number of parallel processors over which to subdivide the y axis of the domain."""

    def __init__(
        self,
        time_step: int,
        n_procs_x: int = 1,
        n_procs_y: int = 1,
    ) -> None:
        """Initialize a Discretization object from basic discretization parameters.

        Parameters:
        -----------
        time_step: int
            The time step with which to run the Component
        n_procs_x: int
           The number of parallel processors over which to subdivide the x axis of the domain.
        n_procs_y: int
           The number of parallel processors over which to subdivide the y axis of the domain.

        Returns:
        --------
        Discretization:
            An initialized Discretization object
        """
        self.time_step = time_step
        self.n_procs_x = n_procs_x
        self.n_procs_y = n_procs_y

    @property
    def n_procs_tot(self) -> int:
        """Total number of processors required by this ROMS configuration."""
        return self.n_procs_x * self.n_procs_y

    def __str__(self) -> str:
        cls_name = self.__class__.__name__

        return textwrap.dedent(
            f"""\
            {cls_name}
            {"-" * len(cls_name)}
            time_step: {self.time_step}s
            n_procs_x: {self.n_procs_x} (Number of x-direction processors)
            n_procs_y: {self.n_procs_y} (Number of y-direction processors)
            """,
        )

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        st = f"{self.time_step=}"
        sx = f"{self.n_procs_x=}" if self.n_procs_x != 1 else ""
        sy = f"{self.n_procs_y=}" if self.n_procs_y != 1 else ""

        # exclude default values from output
        params_s = ", ".join(filter(lambda x: x, (st, sx, sy)))

        return f"{cls_name}({params_s})".replace("self.", "")
