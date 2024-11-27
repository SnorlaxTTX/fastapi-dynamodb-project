from datetime import datetime

from app.core.exceptions import ErrorCode
from app.core.services import BaseService, FileService, LogService

from app.modules.v1.organizations.services.users import UserService


class TaskService(BaseService):
    def __init__(self, table, file_service: FileService, log_service: LogService, user_service: UserService):
        super().__init__(table, pk_prefix="TASK", service_name="Task")
        self.file_service = file_service
        self.log_service = log_service
        self.user_service = user_service

    async def add_user_to_task(self, organization_uuid: str, project_uuid: str, task_uuid: str, user_uuid: str):
        """
        Assign a user to a task in a project.
        If the user is not already in the project, they will be added to the project as well.
        """
        # Step 1: Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")
        user_item = await self.get_item(identifier=organization_uuid, sk=f"USER#{user_uuid}", pk_prefix="ORG")
        await self.get_item(identifier=project_uuid, sk=f"TASK#{task_uuid}", pk_prefix="PROJECT")

        # Step 2: Check if the user is already assigned to the task
        task_user_item = await self.get_item(identifier=task_uuid, sk=f"USER#{user_uuid}", ignore_error=True)
        if task_user_item:
            raise ErrorCode.Conflict("User", user_uuid)  # Raise Conflict if the user is already assigned

        # Step 3: Check if the user is already in the project
        project_user_item = await self.get_item(identifier=project_uuid, sk=f"USER#{user_uuid}", pk_prefix="PROJECT",
                                                ignore_error=True)
        if not project_user_item:
            # Add the user to the project if they are not already part of it
            await self.create_item(
                identifier=project_uuid,
                sk=f"USER#{user_uuid}",
                attributes={"AddedAt": int(datetime.utcnow().timestamp())},
                pk_prefix="PROJECT"
            )

        # Step 4: Assign the user to the task
        await self.create_item(
            identifier=task_uuid,
            sk=f"USER#{user_uuid}",
            attributes={"AddedAt": int(datetime.utcnow().timestamp())}
        )

        return user_item

    # Remove User from Task
    async def remove_user_from_task(self, organization_uuid: str, project_uuid: str, task_uuid: str, user_uuid: str):
        """
        Remove a user from a task in a project.
        """
        # Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")
        await self.get_item(identifier=organization_uuid, sk=f"USER#{user_uuid}", pk_prefix="ORG")
        await self.get_item(identifier=project_uuid, sk=f"TASK#{task_uuid}", pk_prefix="PROJECT")
        await self.get_item(identifier=task_uuid, sk=f"USER#{user_uuid}", pk_prefix="TASK")

        # Delete the item that maps user to task
        return await self.delete_item(identifier=task_uuid, sk=f"USER#{user_uuid}")

    # Get Users in Task
    async def get_users_in_task(self, organization_uuid: str, project_uuid: str, task_uuid: str):
        """
        Retrieve all users assigned to a specific task under a project.
        """
        # Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")
        await self.get_item(identifier=project_uuid, sk=f"TASK#{task_uuid}", pk_prefix="PROJECT")

        # Query for users assigned to this task
        task_users = await self.get_items(identifier=task_uuid, sk_prefix="USER#")

        users = []
        for user_item in task_users:
            user_uuid = user_item['SK']  # Extract user UUID from the SK field

            # Fetch the user details (assuming you have a method to get user info by UUID)
            user_data = await self.get_item(identifier=organization_uuid, sk=user_uuid, pk_prefix="ORG")

            # Add the user data to the list (customize this as per your response structure)
            users.append(user_data)

        return users
