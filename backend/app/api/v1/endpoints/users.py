from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project
from app.schemas import (
    UserResponse, UserUpdate, TeamCreate, TeamUpdate, TeamResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    TeamMemberResponse, PaginatedResponse,
)
from app.core.config import settings

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.avatar is not None:
        current_user.avatar = user_data.avatar
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.is_active == True)
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    users = result.scalars().all()
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Team endpoints
@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.slug == team_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Team slug already exists")
    
    team = Team(
        name=team_data.name,
        slug=team_data.slug,
        description=team_data.description,
        owner_id=current_user.id,
    )
    db.add(team)
    await db.flush()
    
    member = TeamMember(user_id=current_user.id, team_id=team.id, role="owner")
    db.add(member)
    await db.commit()
    await db.refresh(team)
    return team


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Team)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
        .options(selectinload(Team.members).selectinload(TeamMember.user))
    )
    teams = result.scalars().all()
    return teams


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.members).selectinload(TeamMember.user), selectinload(Team.owner))
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    member_result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id)
    )
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    return team


@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Team).where(Team.id == team_id).options(selectinload(Team.members))
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    member_result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id)
    )
    member = member_result.scalar_one_or_none()
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this team")
    
    if team_data.name is not None:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description
    if team_data.avatar is not None:
        team.avatar = team_data.avatar
    
    await db.commit()
    await db.refresh(team)
    return team


@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can delete the team")
    
    await db.delete(team)
    await db.commit()
    return {"message": "Team deleted"}


@router.post("/teams/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(
    team_id: UUID,
    user_id: UUID,
    role: str = "developer",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    member_result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id)
    )
    member = member_result.scalar_one_or_none()
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to add members")
    
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")
    
    new_member = TeamMember(team_id=team_id, user_id=user_id, role=role)
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return new_member


@router.delete("/teams/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    member_result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id)
    )
    member = member_result.scalar_one_or_none()
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to remove members")
    
    if user_id == team.owner_id:
        raise HTTPException(status_code=400, detail="Cannot remove team owner")
    
    target_member = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
    )
    target = target_member.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")
    
    await db.delete(target)
    await db.commit()
    return {"message": "Member removed"}


@router.put("/teams/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
async def update_team_member_role(
    team_id: UUID,
    user_id: UUID,
    role: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    member_result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id)
    )
    member = member_result.scalar_one_or_none()
    if not member or member.role != "owner":
        raise HTTPException(status_code=403, detail="Only owner can change roles")
    
    if user_id == team.owner_id:
        raise HTTPException(status_code=400, detail="Cannot change owner role")
    
    target_member = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
    )
    target = target_member.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")
    
    target.role = role
    await db.commit()
    await db.refresh(target)
    return target