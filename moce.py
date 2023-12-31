import os
import json
import chainlit as cl

from embedchain import Pipeline as App
from datetime import datetime


try:
    HF_TOKEN = os.environ['HUGGINGFACE_API_KEY']
    if HF_TOKEN is None:
        raise ValueError('HUGGINGFACE_API_KEY is not set')
except Exception as err:
    raise(err)


class DatabaseError(Exception):
    pass


class JSONDB:
    def __init__(self, file_path):
        self.file_path = file_path

    def _create_file_if_not_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as fp:
                json.dump([], fp)

    def add_record(self, record):
        try:
            self._create_file_if_not_exists()

            with open(self.file_path, 'r+') as fp:
                try:
                    data = json.load(fp)

                    if record not in data:
                        data.append(record)
                    else:
                        pass
                except Exception as err:
                    print(f'[DEBUG] Error adding record: {str(err)}')
                    raise(err)

                fp.seek(0)
                json.dump(data, fp, indent=4)

        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            raise DatabaseError(f"Error adding record: {str(e)}")

    def get_all_records(self):
        try:            
            with open(self.file_path, 'r') as fp:
                # Attempt to load data, handle empty file scenario
                try:
                    data = json.load(fp)
                except json.JSONDecodeError:
                    data = []

            return data

        except (FileNotFoundError, IOError) as e:
            raise DatabaseError(f"Error getting all records: {str(e)}")

    def get_top_records(self, n):
        try:
            records = self.get_all_records()
            sorted_records = sorted(records, key=lambda x: x.get('added', 0), reverse=True)
            return sorted_records[:n]
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            raise DatabaseError(f"Error getting top records: {str(e)}")


@cl.on_chat_start
async def setup_app():
    app = App.from_config(config_path='data/config.yaml')
    app.collect_metrics = False
    cl.user_session.set('app', app)
    db = JSONDB('data/index.json')
    cl.user_session.set('db', db)


def update_db(data):
    db = cl.user_session.get('db')
    record = {
        'url': data,  # Store the URL as a JSON field
        'added': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    db.add_record(record)


@cl.on_message
async def main(message: cl.Message):
    task_list = cl.TaskList()
    task_list.status = 'Running...'

    app = cl.user_session.get('app')
    msg = cl.Message(content='')

    user_message = message.content

    if user_message.startswith('/add'):
        data = user_message.replace('/add', '').strip()
        db = cl.user_session.get('db')

        records = db.get_all_records()
        if data in [record['url'] for record in records]:
            await cl.Message(
                content='This document already exists in the knowledge base!'
            ).send()
        else:
            add_task = cl.Task(title='Adding to knowledge base', status=cl.TaskStatus.RUNNING)
            await task_list.add_task(add_task)
            await task_list.send()

            app.add(data)
            update_db(data)
            add_task.status = cl.TaskStatus.DONE
            await task_list.send()

            await cl.Message(
                content='Added data to knowledge base!'
            ).send()

    elif user_message.startswith('/kb'):
        kb_task = cl.Task(title='Getting records', status=cl.TaskStatus.RUNNING)
        await task_list.add_task(kb_task)
        await task_list.send()

        data = cl.user_session.get('db').get_top_records(25)
        kb_task.status = cl.TaskStatus.DONE
        await task_list.send()

        if len(data) == 0:
            await cl.Message(
                content='No documents in json index!'
            ).send()

        else:
            markdown_content = "| URL | Added |\n| --- | --- |\n"
            for record in data:
                url = record['url']
                added = record['added']
                markdown_content += f"| {url} | {added} |\n"
            await cl.Message(
                content=markdown_content
            ).send()

    else:
        chat_task = cl.Task(title='Querying LLM', status=cl.TaskStatus.RUNNING)
        await task_list.add_task(chat_task)
        await task_list.send()

        for chunk in await cl.make_async(app.chat)(message.content):
            await msg.stream_token(chunk)

        chat_task.status = cl.TaskStatus.DONE
        await task_list.send()

    await msg.send()

