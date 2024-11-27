from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
from app.core.container import Container
from app.modules.v1.organizations.schemas import (
    OrganizationCreate,
    OrganizationResponse,
    TaskCreate,
    TaskResponse,
    AddTaskUser,
    ProjectCreate,
    ProjectResponse,
    AddProjectUser,
    UserCreate,
    UserResponse,
)

router = APIRouter()


# Organizations CRUD
@router.post("/", response_model=OrganizationResponse, status_code=201)
@inject
async def create_organization(
        payload: OrganizationCreate,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Create a new organization.
    """
    return await service.create_organization(
        name=payload.name, description=payload.description
    )


@router.get("/", response_model=list[OrganizationResponse], status_code=200)
@inject
async def get_all_organizations(
        service=Depends(Provide[Container.organization_service]),
):
    """
    Get all organizations.
    """
    return await service.get_all_organizations()


@router.get("/{organization_uuid}/", response_model=OrganizationResponse, status_code=200)
@inject
async def get_organization(
        organization_uuid: str,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Get organization details by UUID.
    """
    return await service.get_organization(organization_uuid=organization_uuid)


@router.put("/{organization_uuid}/", response_model=OrganizationResponse, status_code=200)
@inject
async def update_organization(
        organization_uuid: str,
        payload: OrganizationCreate,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Update an organization's details by UUID.
    """
    return await service.update_organization(
        organization_uuid=organization_uuid, name=payload.name, description=payload.description
    )


@router.delete("/{organization_uuid}/", status_code=204)
@inject
async def delete_organization(
        organization_uuid: str,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Delete an organization by UUID.
    """
    await service.delete_organization(organization_uuid=organization_uuid)


# Users in Organization
@router.post("/{organization_uuid}/users/", response_model=UserResponse, status_code=201)
@inject
async def create_user_in_organization(
        organization_uuid: str,
        payload: UserCreate,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Create a new user in an organization by UUID.
    """
    return await service.create_user_in_organization(
        organization_uuid=organization_uuid, name=payload.name, email=payload.email, role=payload.role
    )


@router.get("/{organization_uuid}/users/", response_model=list[UserResponse], status_code=200)
@inject
async def get_users_in_organization(
        organization_uuid: str,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Get all users in an organization by UUID.
    """
    return await service.get_organization_users(organization_uuid=organization_uuid)


@router.get("/{organization_uuid}/users/{user_uuid}/", response_model=UserResponse, status_code=200)
@inject
async def get_user_in_organization(
        organization_uuid: str,
        user_uuid: str,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Get details of a specific user by UUID in an organization.
    """
    return await service.get_user_in_organization(organization_uuid=organization_uuid, user_uuid=user_uuid)


@router.put("/{organization_uuid}/users/{user_uuid}/", response_model=UserResponse, status_code=200)
@inject
async def update_user_in_organization(
        organization_uuid: str,
        user_uuid: str,
        payload: UserCreate,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Update a user's details by UUID in an organization.
    """
    return await service.update_user_in_organization(
        organization_uuid=organization_uuid,
        user_uuid=user_uuid,
        name=payload.name,
        email=payload.email,
        role=payload.role,
    )


@router.delete("/{organization_uuid}/users/{user_uuid}/", status_code=204)
@inject
async def delete_user_in_organization(
        organization_uuid: str,
        user_uuid: str,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Delete a user by UUID in an organization.
    """
    await service.delete_user_in_odeleterganization(organization_uuid=organization_uuid, user_uuid=user_uuid)


# Projects in Organization
@router.post("/{organization_uuid}/projects/", response_model=ProjectResponse, status_code=201)
@inject
async def create_project_in_organization(
        organization_uuid: str,
        payload: ProjectCreate,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Create a new project in an organization by UUID.
    """
    return await service.create_project_in_organization(
        organization_uuid=organization_uuid,
        title=payload.title,
        description=payload.description,
        status=payload.status,
    )


@router.get("/{organization_uuid}/projects/", response_model=list[ProjectResponse], status_code=200)
@inject
async def get_projects_in_organization(
        organization_uuid: str,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Get all projects in an organization by UUID.
    """
    return await service.get_organization_projects(organization_uuid=organization_uuid)


@router.get("/{organization_uuid}/projects/{project_uuid}/", response_model=ProjectResponse, status_code=200)
@inject
async def get_project_in_organization(
        organization_uuid: str,
        project_uuid: str,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Get details of a specific project by UUID in an organization.
    """
    return await service.get_project_in_organization(organization_uuid=organization_uuid, project_id=project_uuid)


@router.put("/{organization_uuid}/projects/{project_uuid}/", response_model=ProjectResponse, status_code=200)
@inject
async def update_project_in_organization(
        organization_uuid: str,
        project_uuid: str,
        payload: ProjectCreate,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Update a project's details by UUID in an organization.
    """
    return await service.update_project_in_organization(
        organization_uuid=organization_uuid,
        project_id=project_uuid,
        title=payload.title,
        description=payload.description,
        status=payload.status,
    )


@router.delete("/{organization_uuid}/projects/{project_uuid}/", status_code=204)
@inject
async def delete_project_in_organization(
        organization_uuid: str,
        project_uuid: str,
        service=Depends(Provide[Container.organization_service]),
):
    """
    Delete a project by UUID in an organization.
    """
    await service.delete_project_in_organization(organization_uuid=organization_uuid, project_id=project_uuid)


# Add User to Project
@router.post("/{organization_uuid}/projects/{project_uuid}/users/", response_model=UserResponse, status_code=200)
@inject
async def add_user_to_project(
        organization_uuid: str,
        project_uuid: str,
        payload: AddProjectUser,
        service=Depends(Provide[Container.project_service]),
):
    """
    Add a user to a project within an organization.
    """
    return await service.add_user_to_project(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        user_uuid=str(payload.uuid)
    )


# Remove User from Project
@router.delete("/{organization_uuid}/projects/{project_uuid}/users/{user_uuid}", status_code=204)
@inject
async def remove_user_from_project(
        organization_uuid: str,
        project_uuid: str,
        user_uuid: str,
        service=Depends(Provide[Container.project_service]),
):
    """
    Remove a user from a project within an organization.
    """
    await service.remove_user_from_project(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        user_uuid=user_uuid
    )


# List all Users in a Project
@router.get("/{organization_uuid}/projects/{project_uuid}/users", response_model=list[UserResponse], status_code=200)
@inject
async def get_users_in_project(
        organization_uuid: str,
        project_uuid: str,
        service=Depends(Provide[Container.project_service]),
):
    """
    Get all users assigned to a project in an organization.
    """
    users = await service.get_project_users(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid
    )
    return users


# Get all tasks in a project
@router.get("/{organization_uuid}/projects/{project_uuid}/tasks/", response_model=list[TaskResponse], status_code=200)
@inject
async def get_tasks_in_project(
        organization_uuid: str,
        project_uuid: str,
        service=Depends(Provide[Container.project_service]),
):
    """
    Get all tasks associated with a project in an organization.
    """
    tasks = await service.get_project_tasks(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid
    )
    return tasks


@router.post("/{organization_uuid}/projects/{project_uuid}/tasks/", response_model=TaskResponse, status_code=201)
@inject
async def create_task_in_project(
        organization_uuid: str,
        project_uuid: str,
        payload: TaskCreate = Depends(TaskCreate.as_form),
        service=Depends(Provide[Container.project_service]),
):
    """
    Create a new task under a project within an organization.
    """
    return await service.create_task_in_project(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        deadline=payload.deadline,
        file=payload.file
    )


# Get details of a specific task in a project
@router.get("/{organization_uuid}/projects/{project_uuid}/tasks/{task_uuid}/", response_model=TaskResponse,
            status_code=200)
@inject
async def get_task_in_project(
        organization_uuid: str,
        project_uuid: str,
        task_uuid: str,
        service=Depends(Provide[Container.project_service]),
):
    """
    Get details of a specific task in a project under an organization.
    """
    return await service.get_task_in_project(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        task_uuid=task_uuid,
    )


# Update a task in a project
@router.put("/{organization_uuid}/projects/{project_uuid}/tasks/{task_uuid}/", response_model=TaskResponse,
            status_code=200)
@inject
async def update_task_in_project(
        organization_uuid: str,
        project_uuid: str,
        task_uuid: str,
        payload: TaskCreate,
        service=Depends(Provide[Container.project_service]),
):
    """
    Update a task's details by UUID in a project under an organization.
    """
    return await service.update_task_in_project(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        task_uuid=task_uuid,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        deadline=payload.deadline,
    )


# Delete a task from a project
@router.delete("/{organization_uuid}/projects/{project_uuid}/tasks/{task_uuid}/", status_code=204)
@inject
async def delete_task_in_project(
        organization_uuid: str,
        project_uuid: str,
        task_uuid: str,
        service=Depends(Provide[Container.project_service]),
):
    """
    Delete a task from a project under an organization.
    """
    await service.delete_task_in_project(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        task_uuid=task_uuid
    )


@router.post("/{organization_uuid}/projects/{project_uuid}/tasks/{task_uuid}/users/", response_model=UserResponse,
             status_code=201)
@inject
async def add_user_to_task(
        organization_uuid: str,
        project_uuid: str,
        task_uuid: str,
        payload: AddTaskUser,
        service=Depends(Provide[Container.task_service]),
):
    """
    Add a user to a task in a project under an organization.
    """
    return await service.add_user_to_task(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        task_uuid=task_uuid,
        user_uuid=str(payload.uuid)
    )


@router.delete("/{organization_uuid}/projects/{project_uuid}/tasks/{task_uuid}/users/{user_uuid}/", status_code=204)
@inject
async def remove_user_from_task(
        organization_uuid: str,
        project_uuid: str,
        task_uuid: str,
        user_uuid: str,
        service=Depends(Provide[Container.task_service]),
):
    """
    Remove a user from a task in a project under an organization.
    """
    await service.remove_user_from_task(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        task_uuid=task_uuid,
        user_uuid=user_uuid
    )


@router.get("/{organization_uuid}/projects/{project_uuid}/tasks/{task_uuid}/users/", response_model=list[UserResponse],
            status_code=200)
@inject
async def get_users_in_task(
        organization_uuid: str,
        project_uuid: str,
        task_uuid: str,
        service=Depends(Provide[Container.task_service]),
):
    """
    Get all users assigned to a task in a project under an organization.
    """
    return await service.get_users_in_task(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        task_uuid=task_uuid
    )


@router.get("/{organization_uuid}/projects/{project_uuid}/users/{user_uuid}/tasks/", response_model=list[TaskResponse],
            status_code=200)
@inject
async def get_users_in_task(
        organization_uuid: str,
        project_uuid: str,
        user_uuid: str,
        service=Depends(Provide[Container.user_service]),
):
    """
    Get all users assigned to a task in a project under an organization.
    """
    return await service.get_all_tasks_for_user_in_project(
        organization_uuid=organization_uuid,
        project_uuid=project_uuid,
        user_uuid=user_uuid
    )
