from app.core.services import BaseService, LogService


class UserService(BaseService):
    def __init__(self, table, log_service: LogService):
        super().__init__(table, pk_prefix="", service_name="User")
        self.log_service = log_service

    async def get_all_tasks_for_user_in_project(self, organization_uuid: str, project_uuid: str, user_uuid: str):
        """
        Retrieve all tasks assigned to a specific user in a project under an organization.
        """
        # Verify that the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")

        # Retrieve all tasks in the project
        tasks = await self.get_items(identifier=project_uuid, sk_prefix="TASK", pk_prefix="PROJECT")

        # Now, for each task, check if the user is assigned to it (USER#<UserID> relationship)
        task_user_associations = []
        for task in tasks:
            task_id = task['SK'].split("#")[1]  # Extract Task ID from SK
            user_assigned = await self.get_items(identifier=task_id, sk_prefix="USER", pk_prefix="TASK")

            # Check if the user_uuid is associated with the task
            for user in user_assigned:
                if user['SK'] == f"USER#{user_uuid}":  # If user is assigned to this task
                    task_user_associations.append(task)
                    break

        return task_user_associations
