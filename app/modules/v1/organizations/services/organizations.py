from datetime import datetime

from app.core.services import BaseService, FileService, LogService

from app.modules.v1.organizations.services.projects import ProjectService
from app.utils.constant import GSI_ORG_USERS


class OrganizationService(BaseService):
    def __init__(self, table, file_service: FileService, log_service: LogService, project_service: ProjectService):
        super().__init__(table, pk_prefix="ORG", service_name="Organization")
        self.file_service = file_service
        self.project_service = project_service
        self.log_service = log_service

    # Organizations CRUD
    async def create_organization(self, name: str, description: str):
        """
        Add a new organization.
        """
        organization_uuid = self.generate_uuid()
        attributes = {"Name": name, "Description": description, "CreatedAt": int(datetime.utcnow().timestamp())}
        return await self.create_item(identifier=organization_uuid, sk="META", attributes=attributes)

    async def get_all_organizations(self):
        """
        Retrieve all organizations.
        """
        return await self.get_all_meta()

    async def get_organization(self, organization_uuid: str):
        """
        Get details of a specific organization.
        """
        return await self.get_item(identifier=organization_uuid, sk="META")

    async def update_organization(self, organization_uuid: str, name: str, description: str):
        """
        Update an organization's details.
        """
        attributes = {"Name": name, "Description": description}
        return await self.update_item(identifier=organization_uuid, sk="META", attributes=attributes)

    async def delete_organization(self, organization_uuid: str):
        """
        Delete an organization and all associated data, including tasks, projects, and users.
        """
        # Step 1: Verify the organization exists
        await self.get_organization(organization_uuid)

        # Step 2: Fetch all projects related to the organization and deletion
        projects = await self.get_organization_projects(organization_uuid)
        for project in projects:
            project_uuid = self.extract_uuid(key=project["SK"], prefix="PROJECT")  # Extract project UUID from SK

            # Delete the project itself
            await self.delete_project_in_organization(
                organization_uuid=organization_uuid,
                project_uuid=project_uuid
            )

        # Step 3: Remove all users directly under the organization
        organization_users = await self.get_organization_users(organization_uuid)
        for user in organization_users:
            user_uuid = self.extract_uuid(key=user["SK"], prefix="USER")  # Extract user UUID from SK
            await self.delete_user_in_organization(organization_uuid, user_uuid)

        # Step 4: Delete the organization's meta record
        await self.delete_item(identifier=organization_uuid, sk="META")

    # Users in Organizations
    async def get_organization_users(self, organization_uuid: str):
        """
        Retrieve all users in an organization.
        """
        return await self.get_items(identifier=organization_uuid, sk_prefix="USER#")

    async def create_user_in_organization(self, organization_uuid: str, name: str, email: str, role: str):
        """
        Add a user to an organization.
        """
        user_uuid = self.generate_uuid()
        attributes = {"Name": name, "Email": email, "Role": role, "CreatedAt": int(datetime.utcnow().timestamp())}
        return await self.create_item(identifier=organization_uuid, sk=f"USER#{user_uuid}", attributes=attributes)

    async def get_user_in_organization(self, organization_uuid: str, user_uuid: str):
        """
        Get details of a specific user in an organization.
        """
        return await self.get_item(identifier=organization_uuid, sk=f"USER#{user_uuid}")

    async def update_user_in_organization(self, organization_uuid: str, user_uuid: str, name: str, email: str,
                                          role: str):
        """
        Update a user's details in an organization.
        """
        attributes = {"Name": name, "Email": email, "Role": role}
        return await self.update_item(identifier=organization_uuid, sk=f"USER#{user_uuid}", attributes=attributes)

    async def delete_user_in_organization(self, organization_uuid: str, user_uuid: str):
        """
        Delete a user from an organization and all related data.
        """
        user_sk = f"USER#{user_uuid}"

        # Verify the organization and user exist
        await self.get_item(identifier=organization_uuid, sk=user_sk)

        # Step 1: Fetch all projects in the organization
        project_items = await self.get_items(identifier=organization_uuid, sk_prefix="PROJECT")

        # Step 2: For each project, remove the user from tasks and the project itself
        for project in project_items:
            project_uuid = project["SK"].split("#")[1]  # Extract project UUID from SK
            await self.project_service.remove_user_from_project(organization_uuid, project_uuid, user_uuid)

        # Step 3: Remove the user from the organization
        return await self.delete_item(identifier=organization_uuid, sk=user_sk)

    # Projects in Organizations
    async def get_organization_projects(self, organization_uuid: str):
        """
        Retrieve all projects in an organization.
        """
        return await self.get_items(identifier=organization_uuid, sk_prefix="PROJECT#")

    async def create_project_in_organization(self, organization_uuid: str, title: str, description: str,
                                             status: str):
        """
        Add a project to an organization.
        """
        project_id = self.generate_uuid()
        attributes = {"Title": title, "Description": description, "Status": status,
                      "CreatedAt": int(datetime.utcnow().timestamp())}
        return await self.create_item(identifier=organization_uuid, sk=f"PROJECT#{project_id}", attributes=attributes)

    async def get_project_in_organization(self, organization_uuid: str, project_id: str):
        """
        Get details of a specific project in an organization.
        """
        return await self.get_item(identifier=organization_uuid, sk=f"PROJECT#{project_id}")

    async def update_project_in_organization(self, organization_uuid: str, project_id: str, title: str,
                                             description: str,
                                             status: str):
        """
        Update a project's details in an organization.
        """
        attributes = {"Title": title, "Description": description, "Status": status}
        return await self.update_item(identifier=organization_uuid, sk=f"PROJECT#{project_id}", attributes=attributes)

    async def delete_project_in_organization(self, organization_uuid: str, project_uuid: str):
        """
        Delete a project from an organization and all related data (tasks and task-user relationships).
        """
        # Step 1: Verify the organization and project exist
        await self.get_project_in_organization(organization_uuid, project_uuid)

        # Step 2: Fetch all tasks in the project and delegate deletion
        tasks = await self.project_service.get_project_tasks(organization_uuid=organization_uuid,
                                                             project_uuid=project_uuid)
        for task in tasks:
            task_uuid = self.extract_uuid(task["SK"], prefix="TASK")

            await self.project_service.delete_task_in_project(organization_uuid=organization_uuid,
                                                              project_uuid=project_uuid,
                                                              task_uuid=task_uuid)

        # Step 3: Fetch and delete all users associated with the project
        project_users = await self.project_service.get_project_users(organization_uuid=organization_uuid,
                                                                     project_uuid=project_uuid)
        for user in project_users:
            user_uuid = self.extract_uuid(user["SK"], prefix="USER")
            await self.project_service.remove_user_from_project(organization_uuid=organization_uuid,
                                                                project_uuid=project_uuid, user_uuid=user_uuid)

        # Step 4: Delete the project itself
        return await self.delete_item(identifier=organization_uuid, sk=f"PROJECT#{project_uuid}")
