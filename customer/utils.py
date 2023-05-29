from django.core.serializers.json import DjangoJSONEncoder
from utils.connectors import pick_connector
import sys
import os
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
import io
import json
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from django.conf import settings
from sqlalchemy import create_engine
import logging
import traceback
logging.basicConfig(filename='etl.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

 
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///' + str(settings.DATABASES['default']['NAME']))
}


# create database connection
engine = create_engine('sqlite:///' + str(settings.DATABASES['default']['NAME']))

class PyeScheduler():
    def __init__(self):
        self.scheduler = BackgroundScheduler(jobstores=jobstores) 

    # define a function to pause a job
    def pause_job(self,task):
        query = f"UPDATE apscheduler_jobs SET next_run_time = NULL WHERE id = '{task.job_id}'"
        with engine.connect() as conn:
            result = conn.execute(query)
        logging.info(f"Job with ID {task.job_id} paused")
        task.status = "paused"
        task.save()
        return

        logging.exception(f"Nos job found with ID {task.job_id}")     # define a function to pause a job

    # define a function to remove a job
    def remove_job(self,task):
        query = f"DELETE FROM apscheduler_jobs WHERE id ='{task.job_id}'"
        with engine.connect() as conn:
            result = conn.execute(query)
        logging.info(f"Job with ID {task.job_id} removed")
        task.status = "stopped"
        task.save()
        return

        logging.exception(f"Nos job found with ID {task.job_id}") 

    # define a function to resume a job
    def resume_job(self,task):

        query = f"UPDATE apscheduler_jobs SET next_run_time = 'next_run_time', job_state = 'running' WHERE id = '{task.job_id}'"
        with engine.connect() as conn:
            result = conn.execute(query)

        logging.info(f"Job with ID {task.job_id} resumed")
        task.status = "running"
        task.save()
        return

        logging.exception(f"No job found with ID {task.job_id}")  

    # define a function to stop a job
    def stop_job(self,task):
        query = f"UPDATE apscheduler_jobs SET next_run_time = NULL, job_state = 'stopped' WHERE id = '{task.job_id}'"
        with engine.connect() as conn:
            result = conn.execute(query)

        logging.info(f"Job with ID {task.job_id} stopped")
        task.status = "stopped"
        task.save()
        return
        logging.exception(f"No job found with ID {task.job_id}") 

    

    # define the job scheduling function
    def schedule_job(self,task):    
        print(task.last_run_date,task.last_run_time)
        if task.schedule_time == 'hourly':
            new_job = self.scheduler.add_job(transformer_function, 'interval', minutes=int(task.minute_time), args=[task], jobstore='default')
        elif task.schedule_time == 'daily':
            new_job = self.scheduler.add_job(transformer_function, 'cron', hour=task.daily_time.hour, minute=task.daily_time.minute, args=[task], jobstore='default')
        elif task.schedule_time == 'weekly':
            new_job = self.scheduler.add_job(
                transformer_function,
                'cron',
                hour=task.weekly_time.hour,
                minute=task.weekly_time.minute,
                day_of_week=task.weekly_day,
                day="*", args=[task], jobstore='default'
            )
        else:
            logging.info(f"Instant Job Created, Running...")
            task.status = "running"
            task.save()
            transformer_function(task)

        if task.schedule_time in ["hourly",'daily','weekly']:
            logging.info(f"Job with ID: {new_job.id} scheduled")
            task.job_id = new_job.id
            task.status = "running"
            task.save()
            jobs = self.scheduler.get_jobs(jobstore='default')
            self.scheduler.start()
            print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))



        # try:
        #     # This is here to simulate application activity (which keeps the main thread alive).
        #     while True:
        #         time.sleep(2)
        # except (KeyboardInterrupt, SystemExit):
        #     # Not strictly necessary if daemonic mode is enabled but should be done if possible
        #     self.scheduler.shutdown()



def transformer_function(task):
    try:
        setup_job(task)
        task.status='stopped'
        task.save()
    except Exception as e:
        logging.exception(e)
        task.status='error'
        task.save()

def my_setup_function(task):
    try:
        setup_job(task)
    except Exception as e:
        logging.exception(e)

def run_transform_code(transformer, transform_data, initial_data={}):
    code_str = transformer.code
    result = transform_data
    global source_data
    source_data = initial_data
    # compile the code string
    compiled = compile(code_str, '<string>', 'exec')
    # execute the code in a new namespace
    namespace = {}
    exec(compiled, namespace)
    # check if main function exists in namespace
    if 'main' in namespace:
        # call main function with data argument
        try:
            result = namespace['main'](transform_data)
            return result
        except Exception as e:
            traceback.print_exc()
            raise Exception(e)
    else:
        raise ValueError('No main function found in code') 


def setup_job(task):
    data = {}
    # get all source connection and data 
    source = task.source.all()
    for connector in source:
        con = pick_connector(connector,task)
        data[con.name] = con.get()

    # logging.info(f'source_data: {str(data)}')

    # send source_data to transformer for modification
    transform_data = data
    transformers = task.transformers.all() 
    # logging.exception(f"Transformer Data: {transform_data}")
    for transformer in transformers:   
        try:
            transform_data = run_transform_code(transformer,transform_data,initial_data=data)
        except Exception as e:
            logging.exception(f"Transformer Error: {e}")
            task.status='error'
            task.error = str(e)
            task.save()
            query = f"UPDATE apscheduler_jobs SET next_run_time = NULL, job_state = 'stopped' WHERE id = '{task.job_id}'"
            with engine.connect() as conn:
                result = conn.execute(query)

            raise Exception(e)


    # post transform data to targets for update
    targets = task.targets.all()
    for target in targets:
        con = pick_connector(target,task)
        con.post(transform_data)
 
 




class MyJsonEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, InMemoryUploadedFile):
           return o.read()
        return str(o)


def get_day(day):
    days = {'sun':0,'mon':1,'tue':2,"wed":3,"thu":4,"fri":5,"sat":6}
    return days[day]