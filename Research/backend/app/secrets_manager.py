from .crypto_utils import encrypt_text, decrypt_text
from .security import require_zero_trust
from .models import Secret
from datetime import datetime

class SecretsManager:
    def __init__(self, db):
        self.db = db
    
    def create_secret(self, name: str, value: str, description: str = "", user_id: int = None):
        """Create a new secret"""
        # Check if secret exists
        existing = self.db.query(Secret).filter(Secret.name == name).first()
        if existing:
            raise ValueError(f"Secret '{name}' already exists")
        
        # Encrypt the value
        encrypted = encrypt_text(value)
        
        secret = Secret(
            name=name,
            encrypted_value=encrypted,
            description=description,
            created_by=user_id
        )
        
        self.db.add(secret)
        self.db.commit()
        self.db.refresh(secret)
        
        return secret
    
    def get_secret(self, name: str, decrypt: bool = True):
        """Get secret value"""
        secret = self.db.query(Secret).filter(Secret.name == name).first()
        
        if not secret:
            return None
        
        if decrypt:
            return {
                "id": secret.id,
                "name": secret.name,
                "value": decrypt_text(secret.encrypted_value),
                "description": secret.description
            }
        
        return secret.as_dict()
    
    def rotate_secret(self, name: str, new_value: str):
        """Rotate/update secret value"""
        secret = self.db.query(Secret).filter(Secret.name == name).first()
        
        if not secret:
            raise ValueError(f"Secret '{name}' not found")
        
        secret.encrypted_value = encrypt_text(new_value)
        secret.updated_at = datetime.utcnow()
        
        self.db.commit()
        return secret
