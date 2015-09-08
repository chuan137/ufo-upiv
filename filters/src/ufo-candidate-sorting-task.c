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
 */

#include "ufo-candidate-sorting-task.h"
#include "ufo-ring-coordinates.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#ifdef __APPLE__
#include <OpenCL/cl.h>
#else
#include <CL/cl.h>
#endif


struct _UfoCandidateSortingTaskPrivate {
    cl_kernel found_cand;
    cl_context context;
    guint ring_start;
    guint ring_step;
    guint ring_end;
    guint ring_current;
    gfloat threshold;
};

static void ufo_task_interface_init (UfoTaskIface *iface);

G_DEFINE_TYPE_WITH_CODE (UfoCandidateSortingTask, ufo_candidate_sorting_task, UFO_TYPE_TASK_NODE,
                         G_IMPLEMENT_INTERFACE (UFO_TYPE_TASK,
                                                ufo_task_interface_init))

#define UFO_CANDIDATE_SORTING_TASK_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE((obj), UFO_TYPE_CANDIDATE_SORTING_TASK, UfoCandidateSortingTaskPrivate))

enum {
    PROP_0,
    PROP_RING_START,
    PROP_RING_STEP,
    PROP_RING_END,
    PROP_THRESHOLD,
    N_PROPERTIES
};

static GParamSpec *properties[N_PROPERTIES] = { NULL, };

UfoNode *
ufo_candidate_sorting_task_new (void)
{
    return UFO_NODE (g_object_new (UFO_TYPE_CANDIDATE_SORTING_TASK, NULL));
}

static void
ufo_candidate_sorting_task_setup (UfoTask *task,
                       UfoResources *resources,
                       GError **error)
{
    UfoCandidateSortingTaskPrivate *priv = UFO_CANDIDATE_SORTING_TASK_GET_PRIVATE(task);
    
    priv->found_cand = ufo_resources_get_kernel(resources, "found_cand.cl", NULL, error);

    if (priv->found_cand)
        UFO_RESOURCES_CHECK_CLERR(clRetainKernel(priv->found_cand));

    priv->context = ufo_resources_get_context(resources);
}

static void
ufo_candidate_sorting_task_get_requisition (UfoTask *task,
                                 UfoBuffer **inputs,
                                 UfoRequisition *requisition)
{
    //what should I put here?
    /* input[0] : contrasted image */
    /* input[1] : coordinate list */
    ufo_buffer_get_requisition (inputs[0], requisition);
    printf("I WAS HERE\n");
}

static guint
ufo_candidate_sorting_task_get_num_inputs (UfoTask *task)
{
    return 1;
}

static guint
ufo_candidate_sorting_task_get_num_dimensions (UfoTask *task,
                                             guint input)
{
    return 2;
}

static UfoTaskMode
ufo_candidate_sorting_task_get_mode (UfoTask *task)
{
    return UFO_TASK_MODE_PROCESSOR | UFO_TASK_MODE_GPU;
}

static gboolean
ufo_candidate_sorting_task_process (UfoTask *task,
                         UfoBuffer **inputs,
                         UfoBuffer *output,
                         UfoRequisition *requisition)
{
    UfoCandidateSortingTaskPrivate *priv;
    UfoGpuNode  *node;   
    UfoProfiler *profiler;
    UfoRequisition req;    
    cl_command_queue cmd_queue;
    cl_mem in_mem;
    cl_mem coord;
    cl_mem counter;
    cl_int error;
    unsigned counter_cpu = 0;
    size_t mem_size_c[2];

    priv = UFO_CANDIDATE_SORTING_TASK_GET_PRIVATE (task);
    node = UFO_GPU_NODE (ufo_task_node_get_proc_node (UFO_TASK_NODE (task)));
    cmd_queue = ufo_gpu_node_get_cmd_queue (node);
    profiler = ufo_task_node_get_profiler (UFO_TASK_NODE (task));

    ufo_buffer_get_requisition (inputs[0], &req);
    in_mem = ufo_buffer_get_device_array(inputs[0], cmd_queue);

    mem_size_c[0] = (size_t) req.dims[0];
    mem_size_c[1] = (size_t) req.dims[1];
    
    coord = clCreateBuffer(priv->context, CL_MEM_READ_WRITE,
            sizeof(cl_int) * (2*mem_size_c[0]*mem_size_c[1]), NULL, &error);
    UFO_RESOURCES_CHECK_CLERR(error);

    counter = clCreateBuffer(priv->context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
            sizeof(cl_uint), &counter_cpu, &error);
    UFO_RESOURCES_CHECK_CLERR(error);

    UFO_RESOURCES_CHECK_CLERR(clSetKernelArg(priv->found_cand,0,sizeof(cl_mem),&in_mem));
    UFO_RESOURCES_CHECK_CLERR(clSetKernelArg(priv->found_cand,1,sizeof(cl_mem),&coord));
    UFO_RESOURCES_CHECK_CLERR(clSetKernelArg(priv->found_cand,2,sizeof(cl_mem),&counter));
    UFO_RESOURCES_CHECK_CLERR(clSetKernelArg(priv->found_cand,3,sizeof(float), &(priv->threshold)));

    ufo_profiler_call(profiler,cmd_queue,priv->found_cand,2,mem_size_c,NULL);

    clEnqueueReadBuffer(cmd_queue,counter,CL_TRUE,0,sizeof(cl_uint),&counter_cpu,0,NULL,NULL);

    int* coordinates_cpu = (int*) malloc(sizeof(int) * (2*counter_cpu +2));

    clEnqueueReadBuffer(cmd_queue,coord,CL_TRUE,0,sizeof(cl_int)*counter_cpu*2,coordinates_cpu,0,NULL,NULL);

    UfoRequisition new_req = {.dims[0] = 1+(unsigned)counter_cpu*sizeof(UfoRingCoordinate)/sizeof(float), .n_dims = 1 };   

    URCS* dst = (URCS*) malloc(sizeof(URCS));
    dst->nb_elt = counter_cpu;
    dst->coord = (UfoRingCoordinate*) malloc(sizeof(UfoRingCoordinate) * (counter_cpu));

    g_warning ("counter %d", counter_cpu);

    ufo_buffer_resize(output,&new_req);

    float* res = ufo_buffer_get_host_array(output,NULL);
 
    //Manual memcpy---->> Better debugging
    for(unsigned g = 0; g < counter_cpu;g++)
    {
        dst->coord[g].x = coordinates_cpu[g << 1];
        dst->coord[g].y = coordinates_cpu[(g << 1) +1];
        dst->coord[g].r = priv->ring_current;
    }

    res[0] = (float) dst->nb_elt;
    memcpy (&res[1], dst->coord, (dst->nb_elt) * sizeof (UfoRingCoordinate) );

    UFO_RESOURCES_CHECK_CLERR(clReleaseMemObject(coord));
    UFO_RESOURCES_CHECK_CLERR(clReleaseMemObject(counter));

    if (priv->ring_current + priv->ring_step > priv->ring_end)
        priv->ring_current = priv->ring_start;
    else
        priv->ring_current += priv->ring_step;
  
    free(coordinates_cpu);
    free(dst->coord);
    free(dst);
    return TRUE;
}

static void
ufo_candidate_sorting_task_set_property (GObject *object,
                              guint property_id,
                              const GValue *value,
                              GParamSpec *pspec)
{
    UfoCandidateSortingTaskPrivate *priv = UFO_CANDIDATE_SORTING_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_RING_START:
            priv->ring_start = g_value_get_uint(value);
            priv->ring_current = priv->ring_start;
            break;
        case PROP_RING_STEP:
            priv->ring_step = g_value_get_uint(value);
            break;
        case PROP_RING_END:
            priv->ring_end = g_value_get_uint(value);
            break;
        case PROP_THRESHOLD:
            priv->threshold = g_value_get_float(value);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_candidate_sorting_task_get_property (GObject *object,
                              guint property_id,
                              GValue *value,
                              GParamSpec *pspec)
{
    UfoCandidateSortingTaskPrivate *priv = UFO_CANDIDATE_SORTING_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_RING_START:
            g_value_set_uint (value, priv->ring_start);
            break;
        case PROP_RING_STEP:
            g_value_set_uint (value, priv->ring_step);
            break;
        case PROP_RING_END:
            g_value_set_uint (value, priv->ring_end);
            break;
        case PROP_THRESHOLD:
            g_value_set_float(value, priv->threshold);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_candidate_sorting_task_finalize (GObject *object)
{
    UfoCandidateSortingTaskPrivate *priv = UFO_CANDIDATE_SORTING_TASK_GET_PRIVATE (object);

    if(priv->found_cand)
        UFO_RESOURCES_CHECK_CLERR(clReleaseKernel(priv->found_cand));
    
    G_OBJECT_CLASS (ufo_candidate_sorting_task_parent_class)->finalize (object);
}

static void
ufo_task_interface_init (UfoTaskIface *iface)
{
    iface->setup = ufo_candidate_sorting_task_setup;
    iface->get_num_inputs = ufo_candidate_sorting_task_get_num_inputs;
    iface->get_num_dimensions = ufo_candidate_sorting_task_get_num_dimensions;
    iface->get_mode = ufo_candidate_sorting_task_get_mode;
    iface->get_requisition = ufo_candidate_sorting_task_get_requisition;
    iface->process = ufo_candidate_sorting_task_process;
}

static void
ufo_candidate_sorting_task_class_init (UfoCandidateSortingTaskClass *klass)
{
    GObjectClass *oclass = G_OBJECT_CLASS (klass);

    oclass->set_property = ufo_candidate_sorting_task_set_property;
    oclass->get_property = ufo_candidate_sorting_task_get_property;
    oclass->finalize = ufo_candidate_sorting_task_finalize;

    properties[PROP_RING_START] = 
        g_param_spec_uint ("ring_start",
               "", "",
               1, G_MAXUINT, 5,
               G_PARAM_READWRITE);

    properties[PROP_RING_STEP] = 
        g_param_spec_uint ("ring_step",
               "", "",
               1, G_MAXUINT, 2,
               G_PARAM_READWRITE);

    properties[PROP_RING_END] = 
        g_param_spec_uint ("ring_end",
               "", "",
               1, G_MAXUINT, 5,
               G_PARAM_READWRITE);

    properties[PROP_THRESHOLD] = 
        g_param_spec_float ("threshold",
               "", "",
               G_MINFLOAT, G_MAXFLOAT, 300.0f,
               G_PARAM_READWRITE);

    for (guint i = PROP_0 + 1; i < N_PROPERTIES; i++)
        g_object_class_install_property (oclass, i, properties[i]);

    g_type_class_add_private (oclass, sizeof(UfoCandidateSortingTaskPrivate));
}

static void
ufo_candidate_sorting_task_init(UfoCandidateSortingTask *self)
{
    self->priv = UFO_CANDIDATE_SORTING_TASK_GET_PRIVATE(self);
    self->priv->ring_start = 5;
    self->priv->ring_end = 5;
    self->priv->ring_step = 2;
    self->priv->ring_current = self->priv->ring_start;
    self->priv->threshold = 300.0;
}
