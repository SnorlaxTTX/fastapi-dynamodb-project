from datetime import datetime

from app.core.exceptions import ErrorCode
from app.core.services import BaseService, FileService, LogService
from app.modules.v1.organizations.services.tasks import TaskService


class ProjectService(BaseService):
    def __init__(self, table, file_service: FileService, log_service: LogService, task_service: TaskService):
        super().__init__(table, pk_prefix="PROJECT", service_name="Project")
        self.file_service = file_service
        self.log_service = log_service
        self.task_service = task_service

    async def create_task_in_project(self, organization_uuid: str, project_uuid: str, title: str, description: str,
                                     priority: str, deadline: str, file=None):
        """
        Create a new task under a specific project and organization.
        """
        # Step 1: Verify if the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")

        # Step 2: Generate a unique task UUID
        task_uuid = self.generate_uuid()

        # Step 3: Prepare attributes for the task
        attributes = {
            "Title": title,
            "Description": description,
            "Priority": priority,
            "Deadline": int(deadline.timestamp()),  # Convert to UNIX timestamp
        }

        # Step 4: Handle optional file upload
        if file:
            file_key = f"organizations/{organization_uuid}/projects/{project_uuid}/tasks/{task_uuid}/{file.filename}"
            try:
                file_url = self.file_service.upload_file(file, file_key)  # Upload file using FileService
                attributes["FileUrl"] = file_url  # Add file URL to the task attributes
            except Exception as e:
                raise ErrorCode.BadRequest(f"File upload failed: {str(e)}")

        # Step 5: Create the task in the database
        return await self.create_item(
            identifier=project_uuid,  # Use PROJECT# as PK for tasks
            sk=f"TASK#{task_uuid}",
            attributes=attributes
        )

    async def get_tasks_in_project(self, organization_uuid: str, project_uuid: str):
        """
        Get all tasks associated with a specific project in an organization.
        """
        # Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")

        return await self.get_items(identifier=project_uuid, sk_prefix="TASK#")

    async def get_task_in_project(self, organization_uuid: str, project_uuid: str, task_uuid: str):
        """
        Get details of a specific task in a project under an organization.
        """
        # Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")

        return await self.get_item(identifier=project_uuid, sk=f"TASK#{task_uuid}")

    async def update_task_in_project(self, organization_uuid: str, project_uuid: str, task_uuid: str, title: str,
                                     description: str, priority: str, deadline: str):
        """
        Update a task's details in a specific project under an organization.
        """
        # Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")

        # Update task details
        attributes = {
            "Title": title,
            "Description": description,
            "Priority": priority,
            "Deadline": deadline,
        }
        return await self.update_item(identifier=project_uuid, sk=f"TASK#{task_uuid}", attributes=attributes)

    async def delete_task_in_project(self, organization_uuid: str, project_uuid: str, task_uuid: str):
        """
        Delete a task in a project under an organization, including all user-task relationships.
        """
        # Verify the organization, project, and task exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")
        await self.get_item(identifier=project_uuid, sk=f"TASK#{task_uuid}")

        # Step 1: Fetch and delete all user-task relationships
        user_task_items = await self.task_service.get_items(identifier=task_uuid, sk_prefix="USER")
        for user_task in user_task_items:
            user_sk = user_task["SK"]  # Extract the user SK
            await self.task_service.delete_item(identifier=task_uuid, sk=user_sk)

        # Step 2: If the task has an associated file, delete it
        task = await self.get_item(identifier=project_uuid, sk=f"TASK#{task_uuid}")
        file_url = task.get("FileUrl")
        if file_url:
            self.file_service.delete_file(file_url)

        # Step 3: Delete the task itself
        return await self.delete_item(identifier=project_uuid, sk=f"TASK#{task_uuid}")

    async def get_project_tasks(self, organization_uuid: str, project_uuid: str):
        """
        Retrieve all tasks in a project.
        """
        # Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")

        return await self.get_items(identifier=project_uuid, sk_prefix="TASK#")

    async def get_project_users(self, organization_uuid: str, project_uuid: str):
        """
        Retrieve all users assigned to a project.
        """
        # Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")

        # Query for users assigned to this project
        project_users = await self.get_items(identifier=project_uuid, sk_prefix="USER#")

        users = []
        for user_item in project_users:
            user_uuid = user_item['SK']  # Extract user UUID from the SK field

            # Fetch the user details (assuming you have a method to get user info by UUID)
            user_data = await self.get_item(identifier=organization_uuid, sk=user_uuid, pk_prefix="ORG")

            # Add the user data to the list (customize this as per your response structure)
            users.append(user_data)

        return users

    async def add_user_to_project(self, organization_uuid: str, project_uuid: str, user_uuid: str):
        """
        Add a user to a project.
        """
        # Verify the organization and project exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")
        user_item = await self.get_item(identifier=organization_uuid, sk=f"USER#{user_uuid}", pk_prefix="ORG")

        # Check if the user is already in the project
        project_user_item = await self.get_item(identifier=project_uuid, sk=f"USER#{user_uuid}", ignore_error=True)
        if project_user_item:
            raise ErrorCode.Conflict("User", user_uuid)  # Raise Conflict if the user is already assigned

        user_project_sk = f"USER#{user_uuid}"
        await self.create_item(identifier=project_uuid, sk=user_project_sk,
                               attributes={"AddedAt": int(datetime.utcnow().timestamp())})

        return user_item

    async def remove_user_from_project(self, organization_uuid: str, project_uuid: str, user_uuid: str):
        """
        Remove a user from a project and all associated tasks.
        """
        # Step 1: Verify the organization, project, and user exist
        await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}", pk_prefix="ORG")
        await self.get_item(identifier=organization_uuid, sk=f"USER#{user_uuid}", pk_prefix="ORG")

        # Step 2: Check if the user is in the project
        project_user_item = await self.get_item(identifier=project_uuid, sk=f"USER#{user_uuid}",
                                                ignore_error=True)
        if not project_user_item:
            raise ErrorCode.NotFound("User", user_uuid)

        # Step 3: Fetch all tasks in the project
        task_items = await self.get_items(identifier=project_uuid, sk_prefix="TASK")

        # Step 4: Remove the user from all tasks in the project
        for task in task_items:
            task_uuid = task["SK"].split("#")[1]  # Extract task UUID from SK

            # Check if the user exists in the task
            task_user_item = await self.get_item(identifier=task_uuid, sk=f"USER#{user_uuid}", pk_prefix="TASK",
                                                 ignore_error=True)
            if task_user_item:
                await self.delete_item(identifier=task_uuid, sk=f"USER#{user_uuid}", pk_prefix="TASK")

        # Step 5: Remove the user from the project itself
        return await self.delete_item(identifier=project_uuid, sk=f"USER#{user_uuid}")
