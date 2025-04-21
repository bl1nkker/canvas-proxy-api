from src.jobs.base_queue_service import BaseQueueService


class SourceDataLoadQueueService(BaseQueueService):
    TASK_NAME = "load_data_from_source_job"

    def load_canvas_data(self, user_id: int):
        return self.queue(dict(user_id=user_id), task_name=self.TASK_NAME)
