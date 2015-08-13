#ifndef SUM_TASK_H
#define SUM_TASK_H



void* sum(void *arg);

typedef struct _sum_thread{
    int tid;
    float *ptr;
    unsigned size;
    float *result;
    pthread_mutex_t* mutex;
} sum_thread;


void* sum(void *arg)
{
    sum_thread *data = (sum_thread*) arg;


    if(data->tid % 2 == 0)
    {
        for(unsigned i=0; i < data->size;i++)
        {
            if(data->ptr[i] > 0.001)
            {
                pthread_mutex_lock(data->mutex);
                data->result[i] = data->result[i] + data->ptr[i];
                pthread_mutex_unlock(data->mutex);
            }
            else
            {
                //                printf("UNDER THE THRESHOLLD %f\n", data->ptr[i]);
            }
        }
    }
    else
    {

        for(int i=data->size; i >= 0; i--)
        {
            if(data->ptr[i] > 0.001)
            {
                pthread_mutex_lock(data->mutex);

                data->result[i] = data->result[i] + data->ptr[i];
                pthread_mutex_unlock(data->mutex);

            }
        }

    }


    pthread_exit(NULL);



}




#endif 
