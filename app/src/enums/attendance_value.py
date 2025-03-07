import enum


class AttendanceValue(enum.Enum):
    COMPLETE = "complete"  # tick
    INCOMPLETE = "incomplete"  # x-mark
    EXCUSE = "excuse"  # uvazh
