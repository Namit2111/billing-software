"""
Organization service
"""
from typing import Optional, Dict, Any
from supabase import Client

from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.core.exceptions import NotFoundError, ForbiddenError


class OrganizationService:
    """Service for organization operations"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.org_repo = OrganizationRepository(supabase)
        self.user_repo = UserRepository(supabase)
    
    async def create(
        self,
        name: str,
        owner_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new organization
        
        Args:
            name: Organization name
            owner_id: User ID of the owner
            **kwargs: Additional organization fields
            
        Returns:
            Created organization
        """
        # Create organization
        org_data = {
            "name": name,
            **kwargs
        }
        org = await self.org_repo.create(org_data)
        
        # Update user to be owner of this organization
        await self.user_repo.update_organization(
            owner_id,
            org["id"],
            role="owner"
        )
        
        return org
    
    async def get(self, organization_id: str) -> Dict[str, Any]:
        """Get organization by ID"""
        org = await self.org_repo.get_by_id(organization_id)
        if not org:
            raise NotFoundError("Organization", organization_id)
        return org
    
    async def update(
        self,
        organization_id: str,
        user_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update organization
        
        Args:
            organization_id: Organization UUID
            user_id: User ID making the update
            data: Fields to update
            
        Returns:
            Updated organization
        """
        # Verify user is owner
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.get("organization_id") != organization_id:
            raise ForbiddenError("You don't have access to this organization")
        
        if user.get("role") != "owner":
            raise ForbiddenError("Only organization owners can update settings")
        
        # Update organization
        updated = await self.org_repo.update(organization_id, data)
        if not updated:
            raise NotFoundError("Organization", organization_id)
        
        return updated
    
    async def upload_logo(
        self,
        organization_id: str,
        file_content: bytes,
        filename: str
    ) -> str:
        """
        Upload organization logo
        
        Args:
            organization_id: Organization UUID
            file_content: Logo file bytes
            filename: Original filename
            
        Returns:
            URL of uploaded logo
        """
        # Upload to Supabase Storage
        storage_path = f"logos/{organization_id}/{filename}"
        
        self.supabase.storage.from_("assets").upload(
            storage_path,
            file_content,
            {"content-type": "image/png"}
        )
        
        # Get public URL
        url = self.supabase.storage.from_("assets").get_public_url(storage_path)
        
        # Update organization
        await self.org_repo.update_logo(organization_id, url)
        
        return url
    
    async def get_members(self, organization_id: str) -> list:
        """Get all members of an organization"""
        return await self.user_repo.get_by_organization(organization_id)
    
    async def invite_member(
        self,
        organization_id: str,
        email: str,
        role: str = "member"
    ) -> Dict[str, Any]:
        """
        Invite a new member to organization
        
        Args:
            organization_id: Organization UUID
            email: Email to invite
            role: Role to assign
            
        Returns:
            Invitation data
        """
        # For now, just create a pending invitation record
        # In production, this would send an invitation email
        return {
            "email": email,
            "role": role,
            "organization_id": organization_id,
            "status": "pending"
        }
    
    async def get_next_invoice_number(self, organization_id: str) -> str:
        """Get the next invoice number for the organization"""
        return await self.org_repo.get_next_invoice_number(organization_id)
    
    async def increment_invoice_number(self, organization_id: str) -> int:
        """Increment and get the next invoice number"""
        return await self.org_repo.increment_invoice_number(organization_id)

