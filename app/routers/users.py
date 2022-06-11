from typing import Optional

from fastapi import APIRouter, Request, Response

from app.schemas import RegisterValidator

router = APIRouter(
    prefix='/users',
)


@router.post('/register')
def register_user(user: RegisterValidator, response: Response) -> None:
    response.set_cookie(key='X-Authorization', value=user.username, httponly=True)


@router.get('/current_user')
def get_user(request: Request) -> Optional[str]:
    return request.cookies.get('X-Authorization')
