import enum


class AttendanceStatus(enum.Enum):
    INITIATED = "INITIATED"  # tick
    IN_PROGRESS = "IN_PROGRESS"  # x-mark
    COMPLETED = "COMPLETED"  # uvazh
