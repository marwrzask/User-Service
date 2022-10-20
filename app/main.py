""" Unnessesary modules """
import aio_pika
import json
from fastapi import FastAPI, Query, status, Request, Response, BackgroundTasks
from fastapi_redis_cache import FastApiRedisCache, cache
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from pydantic import EmailStr
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Optional
from app.schemas import User, UserWithOutId, UserEvent
from app.utils import delete_cache

SQL_DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"
REDIS_CONNECTION_STRING = "redis://redis:6379"
engine = create_engine(SQL_DATABASE_URL, echo=True)


def create_table():
    SQLModel.metadata.create_all(engine)


'''def get_session():
    with Session(engine) as session:
        yield session
'''


async def publish_message(msg):
    connection = await aio_pika.connect("amqp://rabbitmq")

    async with connection:
        queue_name = "users_queue"
        channel = await connection.channel()
        await channel.declare_queue(queue_name, auto_delete=True)

        message = aio_pika.Message(body=json.dumps(msg.dict()).encode())
        await channel.default_exchange.publish(message, routing_key=queue_name)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_table()
    redis_cache = FastApiRedisCache()
    redis_cache.init(host_url=REDIS_CONNECTION_STRING, prefix="users_cache",
                     response_header="X-Users_cache",
                     ignore_arg_types=[Request, Response, Session])


'''@app.on_event("shutdown")
def app_shutdown():
    '''

responses = {400: {'description': 'Invalid Parameter Received'},
             404: {'description': 'User Not Found'},
             405: {'description': 'Method Not Allowed'},
             500: {'description': 'Internal Server Error'},
             503: {'description': 'Service Unavailable'}
             }


@app.post('/v1/users',
          summary="Create a new user account",
          description='Create a user account with all the information',
          response_model=User,
          status_code=201,
          responses=responses)
async def add_new_user(user: UserWithOutId, background_tasks: BackgroundTasks):
    """ Create a new user and store in user database"""
    with Session(engine) as session:
        user = User.from_orm(user)
        session.add(user)
        session.commit()
        session.refresh(user)
    user_event = UserEvent(action_type="Post User", user_dict=user.dict())
    background_tasks.add_task(publish_message, user_event)
    return user


@app.get('/v1/users/{id}',
         summary='Get user info',
         description='Get user info by id',
         response_model=User,
         status_code=200,
         responses=responses
         )
@cache(expire=120)
async def get_user_info(id: int):
    """ Get information about the user, search by id"""
    with Session(engine) as session:
        statement = select(User).where(User.id == id)
        user_id = session.exec(statement).one_or_none()

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with ID={id} not found")
        else:
            encoded_user = jsonable_encoder(user_id)

    return encoded_user


@app.delete('/v1/users/{id}',
            summary="Delete user",
            description='Delete user by id',
            status_code=200,
            responses=responses
            )
async def delete_user(id: int, background_tasks: BackgroundTasks):
    """ Delete user from the database, search be id"""
    with Session(engine) as session:
        statement = select(User).where(User.id == id)
        user = session.exec(statement).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with ID={id} not found")
        user_to_notify = user
        session.delete(user)
        session.commit()
    user_event = UserEvent(action_type="Delete User", user_dict=user_to_notify.dict())
    background_tasks.add_task(publish_message, user_event)

    delete_cache(user)
    return user


@app.put('/v1/users/{id}',
         summary="Update user info",
         description='Update user into by id',
         status_code=200,
         response_model=User,
         responses=responses)
async def update_user_info(id: int, user: UserWithOutId, background_tasks: BackgroundTasks):
    """ Update information about the user, search by id"""
    with Session(engine) as session:
        user_to_update = session.get(User, id)
        if user_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with ID={id} not found")
        user_dict = user.dict(exclude_unset=True)
        for key, value in user_dict.items():
            setattr(user_to_update, key, value)
        session.add(user_to_update)
        session.commit()
        session.refresh(user_to_update)

    user_event = UserEvent(action_type="Put User", user_dict=user_to_update.dict())
    background_tasks.add_task(publish_message, user_event)
    delete_cache(user_to_update)
    return user_to_update


""" statement = select(User).where(User.id == id)
        user_to_update = session.exec(statement).first()"""


@app.get('/v1/users',
         summary='Search and filter users',
         description='Search and filter users by id, nickname or email. Search parameters are mutually exclusive. '
                     'If no query parameters indicated - returns all available users sorted by id.',
         status_code=200,
         responses=responses
         )
@cache(expire=120)
async def search_user(id: Optional[list[int]] = Query(default=None),
                      nickname: Optional[str] = Query(default=None),
                      email: Optional[EmailStr] = Query(default=None)):
    """ Search user by id, nickname or email, if none function return list of users"""
    if [id, nickname, email].count(None) >= 2:

        if id:
            with Session(engine) as session:
                user_list = []
                for i in range(len(id)):
                    statement = select(User).where(User.id == id[i])
                    user_all = session.exec(statement).first()
                    encoded_user = jsonable_encoder(user_all)
                    user_list.append(encoded_user)
            return user_list

        if nickname:
            with Session(engine) as session:
                statement = select(User).where(User.nickname == nickname)
            user = session.exec(statement).first()
            encoded_user = jsonable_encoder(user)
            return encoded_user

        if email:
            with Session(engine) as session:
                statement = select(User).where(User.email == email)
            user = session.exec(statement).first()
            encoded_user = jsonable_encoder(user)
            return encoded_user

        with Session(engine) as session:
            statement = select(User)
        user = session.exec(statement).all()
        encoded_user = jsonable_encoder(user)
        return encoded_user
    else:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Metod not allowed')
