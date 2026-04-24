from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.core.security import verify_password
from app.models.user import User
from app.models.profile import Profile
from app.core.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return profile


def require_role(*allowed_roles: UserRole):
    def role_checker(current_profile: Profile = Depends(get_current_profile)):
        if current_profile.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )
        return current_profile
    return role_checker


def require_admin(current_profile: Profile = Depends(require_role(UserRole.ADMIN))) -> Profile:
    return current_profile
