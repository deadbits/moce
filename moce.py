import os
import chainlit as cl

from embedchain import Pipeline as App
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from datetime import datetime

try:
    HF_TOKEN = os.environ['HUGGINGFACE_API_KEY']
    if HF_TOKEN is None:
        raise ValueError('HUGGINGFACE_API_KEY is not set')
except Exception as err:
    raise(err)


@cl.on_chat_start
async def setup_app():
    app = App.from_config(config_path='data/config.yaml')
    app.collect_metrics = False
    cl.user_session.set('app', app)

    db = TinyDB('data/index.json',
        storage=CachingMiddleware(JSONStorage)
    )
    db_table = db.table('index')
    cl.user_session.set('jdb', db_table)


def update_db(data):
    db = cl.user_session.get('jdb')
    db.insert({
        'document': data,
        'added': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })


def get_last_added():
    db = cl.user_session.get('jdb')
    data = db.all()
    print(f'DEBUG: KB: {data}')
    reversed_entries = list(reversed(list(data.items())))
    result = dict(reversed_entries[:25])
    return result


@cl.on_message
async def main(message: cl.Message):
    task_list = cl.TaskList()
    task_list.status = 'Running...'

    app = cl.user_session.get('app')
    msg = cl.Message(content='')

    user_message = message.content
    print(user_message)

    if user_message.startswith('/add'):

        add_task = cl.Task(title='Adding to knowledge base', status=cl.TaskStatus.RUNNING)
        await task_list.add_task(add_task)
        await task_list.send()

        data = user_message.replace('/add', '')
        app.add(data)
    
        add_task.status = cl.TaskStatus.DONE
        await task_list.send()

        await cl.Message(
            content='Added data to knowledge base!'
        ).send()

    elif user_message.startswith('/kb'):
        kb_task = cl.Task(title='Getting records', status=cl.TaskStatus.RUNNING)
        await task_list.add_task(kb_task)
        await task_list.send()

        data = get_last_added()
        kb_task.status = cl.TaskStatus.DONE
        await task_list.send()

    else:
        chat_task = cl.Task(title='Querying LLM', status=cl.TaskStatus.RUNNING)
        await task_list.add_task(chat_task)
        await task_list.send()

        for chunk in await cl.make_async(app.chat)(message.content):
            await msg.stream_token(chunk)

        chat_task.status = cl.TaskStatus.DONE
        await task_list.send()

    await msg.send()

