/*
 * Copyright (C) 2011-2015 Karlsruhe Institute of Technology
 *
 * This file is part of Ufo.
 *
 * This library is free software: you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation, either
 * version 3 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Authored by: Kevin Höfle (kevinahoefle@gmail.com)
 */




#ifdef __APPLE__
#include <OpenCL/cl.h>
#else
#include <CL/cl.h>
#endif


#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "ufo-contrast-task.h"


#include <pthread.h>
#include <threads/contrast_task.h>

struct _UfoContrastTaskPrivate {

    cl_context context;
    cl_kernel cut_kernel;
    gfloat sigma_top;
    gfloat sigma_bottom;
    gboolean remove_high;


};


static void ufo_task_interface_init (UfoTaskIface *iface);

G_DEFINE_TYPE_WITH_CODE (UfoContrastTask, ufo_contrast_task, UFO_TYPE_TASK_NODE,
        G_IMPLEMENT_INTERFACE (UFO_TYPE_TASK,
            ufo_task_interface_init))

#define UFO_CONTRAST_TASK_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE((obj), UFO_TYPE_CONTRAST_TASK, UfoContrastTaskPrivate))

    enum {
        PROP_0,
        PROP_SIGMA_TOP,
        PROP_SIGMA_BOTTOM,
        N_PROPERTIES
    };

static GParamSpec *properties[N_PROPERTIES] = { NULL, };

    UfoNode *
ufo_contrast_task_new (void)
{
    return UFO_NODE (g_object_new (UFO_TYPE_CONTRAST_TASK, NULL));
}

    static void
ufo_contrast_task_setup (UfoTask *task,
        UfoResources *resources,
        GError **error)
{
    UfoContrastTaskPrivate* priv;
    priv = UFO_CONTRAST_TASK_GET_PRIVATE (task);
    priv->cut_kernel = ufo_resources_get_kernel(resources, "cut_sigma.cl",NULL,error); 
    priv->context = ufo_resources_get_context(resources);

    if(priv->cut_kernel)
    {
        UFO_RESOURCES_CHECK_CLERR(clRetainKernel(priv->cut_kernel));
    }


}

    static void
ufo_contrast_task_get_requisition (UfoTask *task,
        UfoBuffer **inputs,
        UfoRequisition *requisition)
{
    ufo_buffer_get_requisition(inputs[0], requisition);
}

    static guint
ufo_contrast_task_get_num_inputs (UfoTask *task)
{
    return 1;
}

    static guint
ufo_contrast_task_get_num_dimensions (UfoTask *task,
        guint input)
{
    return 2;
}

    static UfoTaskMode
ufo_contrast_task_get_mode (UfoTask *task)
{
    return UFO_TASK_MODE_PROCESSOR | UFO_TASK_MODE_GPU;
}


static int get_pos(int x,int y,int w,int offset)
{
    return x+y*w + offset;
}



static int test_area(int refpoint, int alt, int start,int real)
{
    if(start + alt >= real)
    {
        printf("INDEX EXCEEDS MATRIX DIMENSION! CHANGING SIZE FROM %d to %d\n",alt,real - start);
        return real - start;
    }
    else
    {
        return alt;
    }
}

static float get_mean(float* input, unsigned counter, int* coordinates)
{
    float mean = 0;
    if(coordinates != NULL)
    { 
        for(unsigned i = 0; i < counter;i++)
        {
            mean += input[coordinates[i]];
        }
    }
    else
    {
        for(unsigned i = 0; i < counter; i++)
        {
            mean += input[i];
        }
    } 
    return (mean/counter);
}

static float get_std(float* input, unsigned counter, float mean,int* coordinates)
{
    float std = 0;


    if(coordinates != NULL)
    {
        for(unsigned i = 0; i < counter; i ++)
        {
            std += pow(input[coordinates[i]] - mean,2);
        }
    }
    else
    {
        for(unsigned i = 0; i < counter; i++)
        {
            std += pow(input[i] - mean,2);
        }
    }
    
    return (sqrt((std/counter)));
}




static void thresh_counter(float* input,unsigned * counter, int* coordinates,float top_cut,float bottom_cut,int k)
{
    for(unsigned i=0; i < counter[k-1]; i++)
    {
        if(input[coordinates[i]] >= top_cut || input[coordinates[i]] <= bottom_cut)
        {
            input[coordinates[i]] = 0;
        }
        else
        {
            coordinates[counter[k]] = coordinates[counter[k]];
            counter[k]++;
        }
    }

}



    static gboolean
ufo_contrast_task_process (UfoTask *task,
        UfoBuffer **inputs,
        UfoBuffer *output,
        UfoRequisition *requisition)
{
    UfoContrastTaskPrivate *priv = UFO_CONTRAST_TASK_GET_PRIVATE (task);
    UfoRequisition input_req;
    ufo_buffer_get_requisition (inputs[0], &input_req);


    UfoGpuNode *node;
    UfoProfiler *profiler;
    cl_command_queue cmd_queue;


    cl_mem in_mem_gpu;
    cl_mem out_mem_gpu;
    gsize mem_size_c;


    node = UFO_GPU_NODE (ufo_task_node_get_proc_node (UFO_TASK_NODE (task)));
    cmd_queue = ufo_gpu_node_get_cmd_queue (node);

    profiler = ufo_task_node_get_profiler (UFO_TASK_NODE (task));


    gfloat* in_mem = ufo_buffer_get_host_array(inputs[0], NULL);
    in_mem_gpu = ufo_buffer_get_device_array(inputs[0],cmd_queue);

    out_mem_gpu = ufo_buffer_get_device_array(output,cmd_queue);




    float mean = 0;
    float std = 0;
    float top_cut;
    float bottom_cut;
    float tmp_std;
    float tmp_mean;

    unsigned alt_amount;
    unsigned real_amount;

    
    unsigned h = input_req.dims[0];
    unsigned w = input_req.dims[1];

    unsigned alt_h = 400;
    unsigned alt_w = 400;

    unsigned start_x = 500; //where in the line
    unsigned start_y = 500; //which line

    unsigned ref_point = get_pos(start_x,start_y,w,0);

    float init_top  = priv->sigma_top;
    float init_bottom = priv->sigma_bottom;


    real_amount = (input_req.dims[1] * input_req.dims[0]);
    alt_amount = alt_h*alt_w;

    int coordinates[real_amount]; 

    alt_h = test_area(ref_point, alt_h,start_y,h);
    alt_w = test_area(ref_point, alt_w,start_x,w);

    unsigned cnt[100];

    
    //At each loop the std will be calculated on a new data set which were cut in the 
    //loop before till the change is not over a certain percantage (5%)

    for(unsigned k = 0; k < 100; k++)
    {
        //compute mean
        mean = 0;
        std = 0;
        cnt[k] = 0;

        //First calculation
        if(k==0)
        {

            //The first calculation still works with the normal x,y coordinates
            
            //Calculate Mean:
            for(unsigned i = 0; i < alt_h; i++)
            {
                for(unsigned j = 0; j < alt_w; j++)
                {
                    mean += in_mem[get_pos(j,i,w,ref_point)];
                }
            }

            mean /= alt_amount;

            //STD Derivation
            for(unsigned i = 0; i < alt_h; i++)
            {
                for(unsigned j = 0; j < alt_w; j++)
                {       
                    std += pow(in_mem[get_pos(j,i,w,ref_point)] - mean,2);
                }      
            }

            std = sqrt((std/(alt_amount)));
        }
        else
        {
            //All calculations after first one
            //Updating the mean and the std

            mean = get_mean(in_mem,cnt[k-1],coordinates);
            std = get_std(in_mem, cnt[k-1], mean, coordinates);
        }

        //Check old std to new
        if(std == 0)
        {
            break;
        }

        if(k == 0)
        {
            tmp_std = std;
        }
        else
        {
            //if the std derivation does not change much anyome stop execution
            if(fabs(tmp_std - std)/tmp_std < 0.09)
            { 
                break;
            }   
        }

        //Adjust the window
        top_cut = mean + (init_top/(k+1))*std;
        bottom_cut = mean - (init_bottom/(k+1))*std;

        if(k == 0)
        {
            //First calculation
            for(unsigned i = 0; i < alt_h; i++)
            {
                for(unsigned j = 0; j < alt_w; j++)
                {
                    if((in_mem[get_pos(j,i,w,ref_point)] >= top_cut) || (in_mem[get_pos(j,i,w,ref_point)] <= bottom_cut))
                    {
                        in_mem[get_pos(j,i,w,ref_point)] = 0;
                    }
                    else
                    {
                        //Save coordinates that are not zero for the next iteration
                        coordinates[cnt[k]] = get_pos(j,i,w,ref_point);
                        cnt[k]++;;
                    }
                }
            }
        }
        else
        {
            //Thresh the picture according to the window and count how many parts are not zero (in cnt[k]
            thresh_counter(in_mem,cnt,coordinates,top_cut,bottom_cut,k);

            //check if values are all set to zero, if yes stop execution
            if(cnt[k] == 0)
            {
                break; 
            }  
            else
            {
                //Update tmp std and tmp mean
                tmp_std = std;
                tmp_mean = mean;
            } 

        }
    }


    //use the found mean and std to adjust the right threshhold
    bottom_cut = tmp_mean + 2*tmp_std;
    top_cut = tmp_mean +  5*tmp_std;

    mem_size_c = (gsize) real_amount;

    
    //Do threshhold on the whole picture  on GPU
    UFO_RESOURCES_CHECK_CLERR(clSetKernelArg(priv->cut_kernel,0,sizeof(cl_mem), &in_mem_gpu));
    UFO_RESOURCES_CHECK_CLERR(clSetKernelArg(priv->cut_kernel,1,sizeof(cl_mem), &out_mem_gpu));
    UFO_RESOURCES_CHECK_CLERR(clSetKernelArg(priv->cut_kernel,2,sizeof(cl_float), &top_cut));
    UFO_RESOURCES_CHECK_CLERR(clSetKernelArg(priv->cut_kernel,3,sizeof(cl_float), &bottom_cut));


    ufo_profiler_call(profiler,cmd_queue, priv->cut_kernel,1,&mem_size_c,NULL);



    return TRUE;
}

    static void
ufo_contrast_task_set_property (GObject *object,
        guint property_id,
        const GValue *value,
        GParamSpec *pspec)
{
    UfoContrastTaskPrivate *priv = UFO_CONTRAST_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_SIGMA_TOP:
            priv->sigma_top = g_value_get_float(value);
            break;


        case PROP_SIGMA_BOTTOM:
            priv->sigma_bottom = g_value_get_float(value);
            break;   
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

    static void
ufo_contrast_task_get_property (GObject *object,
        guint property_id,
        GValue *value,
        GParamSpec *pspec)
{
    UfoContrastTaskPrivate *priv = UFO_CONTRAST_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_SIGMA_TOP:
            g_value_set_float(value, priv->sigma_top);
            break;

        case PROP_SIGMA_BOTTOM:
            g_value_set_float(value,priv->sigma_bottom);

        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

    static void
ufo_contrast_task_finalize (GObject *object)
{
    UfoContrastTaskPrivate *priv;
    priv = UFO_CONTRAST_TASK_GET_PRIVATE(object);

    if(priv->cut_kernel)
    {
        UFO_RESOURCES_CHECK_CLERR(clReleaseKernel(priv->cut_kernel));
    }


    G_OBJECT_CLASS (ufo_contrast_task_parent_class)->finalize (object);
}

    static void
ufo_task_interface_init (UfoTaskIface *iface)
{
    iface->setup = ufo_contrast_task_setup;
    iface->get_num_inputs = ufo_contrast_task_get_num_inputs;
    iface->get_num_dimensions = ufo_contrast_task_get_num_dimensions;
    iface->get_mode = ufo_contrast_task_get_mode;
    iface->get_requisition = ufo_contrast_task_get_requisition;
    iface->process = ufo_contrast_task_process;
}

    static void
ufo_contrast_task_class_init (UfoContrastTaskClass *klass)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS (klass);

    gobject_class->set_property = ufo_contrast_task_set_property;
    gobject_class->get_property = ufo_contrast_task_get_property;
    gobject_class->finalize = ufo_contrast_task_finalize;

    properties[PROP_SIGMA_TOP] =
        g_param_spec_float ("sigma_top",
                "defines the window size, thus the threshold",
                "defines the widnow size, thus the threshold",
                1, G_MAXFLOAT, 10,
                G_PARAM_READWRITE);

    properties[PROP_SIGMA_BOTTOM] =
        g_param_spec_float ("sigma_bottom",
                "defines the window size, thus the threshold",
                "defines the widnow size, thus the threshold",
                -10, G_MAXFLOAT, 10,
                G_PARAM_READWRITE);




    for (guint i = PROP_0 + 1; i < N_PROPERTIES; i++)
        g_object_class_install_property (gobject_class, i, properties[i]);

    g_type_class_add_private (gobject_class, sizeof(UfoContrastTaskPrivate));
}

    static void
ufo_contrast_task_init(UfoContrastTask *self)
{
    self->priv = UFO_CONTRAST_TASK_GET_PRIVATE(self);
    self->priv->remove_high = 0;
}
