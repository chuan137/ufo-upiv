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

#include "ufo-piv-contrast-task.h"
#include <stdio.h>
#include <math.h>


struct _UfoPivContrastTaskPrivate {
    gboolean foo;
};

static void ufo_task_interface_init (UfoTaskIface *iface);

G_DEFINE_TYPE_WITH_CODE (UfoPivContrastTask, ufo_piv_contrast_task, UFO_TYPE_TASK_NODE,
                         G_IMPLEMENT_INTERFACE (UFO_TYPE_TASK,
                                                ufo_task_interface_init))

#define UFO_PIV_CONTRAST_TASK_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE((obj), UFO_TYPE_PIV_CONTRAST_TASK, UfoPivContrastTaskPrivate))

enum {
    PROP_0,
    PROP_TEST,
    N_PROPERTIES
};

static GParamSpec *properties[N_PROPERTIES] = { NULL, };

UfoNode *
ufo_piv_contrast_task_new (void)
{
    return UFO_NODE (g_object_new (UFO_TYPE_PIV_CONTRAST_TASK, NULL));
}

static void
ufo_piv_contrast_task_setup (UfoTask *task,
                       UfoResources *resources,
                       GError **error)
{
}

static void
ufo_piv_contrast_task_get_requisition (UfoTask *task,
                                 UfoBuffer **inputs,
                                 UfoRequisition *requisition)
{
    ufo_buffer_get_requisition(inputs[0], requisition);
}

static guint
ufo_piv_contrast_task_get_num_inputs (UfoTask *task)
{
    return 1;
}

static guint
ufo_piv_contrast_task_get_num_dimensions (UfoTask *task,
                                             guint input)
{
    return 2;
}

static UfoTaskMode
ufo_piv_contrast_task_get_mode (UfoTask *task)
{
    return UFO_TASK_MODE_PROCESSOR | UFO_TASK_MODE_CPU;
}

static float array_min(float *data, int size) 
{
    float res = data[0];
    for (int i = 1; i < size; i++) 
    {
        if (data[i] < res) res = data[i];
    }
    return res;
}

static float array_max(float *data, int size) 
{
    float res = data[0];
    for (int i = 1; i < size; i++) 
    {
        if (data[i] > res) res = data[i];
    }
    return res;
}

static float array_mean(float *data, int size, float low, float high) 
{
    float res = 0.0f;
    unsigned ct = 0;
    for (int i = 0; i < size; i++) {
        if (data[i] > low && data[i] < high) {
            res += data[i];
            ct++;
        }
    }
    return res/ct;
}

static float array_std(float *data, int size, float mean, float low, float high)
{
    float res = 0.0f;
    unsigned ct = 0;
    for (int i = 0; i < size; i++) {
        if (data[i] > low && data[i] < high) {
            res += (data[i]-mean) * (data[i]-mean);
            ct++;
        }
    }
    return sqrt(res/ct);
}

static float sigmoid(float x, float mean, float sigma, float gamma)
{
    float f1, f2;
    if (x < mean + 0.25*sigma || x > mean + 10*sigma) {
        f1 = 0.0;
        f2 = 1.0;
    }
    else {
        f1 = 1.0 - 1.0 / (1.0 + exp( (x - mean - 1.0*sigma) / sigma ));
        f2 = pow(x, gamma);
    }
    return f1*f2;
}

static gboolean
ufo_piv_contrast_task_process (UfoTask *task,
                         UfoBuffer **inputs,
                         UfoBuffer *output,
                         UfoRequisition *requisition)
{
    UfoRequisition input_req;
    ufo_buffer_get_requisition(inputs[0], &input_req);

    unsigned offset_x = input_req.dims[0] / 4;
    unsigned offset_y = input_req.dims[1] / 4;
    unsigned len_x = input_req.dims[0] / 4;
    unsigned len_y = input_req.dims[1] / 4;

    if ((len_x + offset_x) > input_req.dims[0])
        len_x = input_req.dims[0] - offset_x;
    if ((len_y + offset_y) > input_req.dims[0])
        len_y = input_req.dims[1] - offset_y;

    gfloat *in_mem = ufo_buffer_get_host_array(inputs[0], NULL);
    gfloat *out_mem = ufo_buffer_get_host_array(output, NULL);
    gfloat *test_mem = g_malloc0 (len_x*len_y*sizeof(gfloat));

    for (unsigned i = 0; i < len_x; i++) 
    {
        for (unsigned j = 0; j < len_y; j++) 
        {
            unsigned id = i * len_x + j;
            unsigned id_0 = (i+offset_x) * input_req.dims[0] + (j+offset_y);
            test_mem[id] = in_mem[id_0];
        }
    }

    int n = len_x * len_y;
    int ct = 0;
    float low_cut=0, high_cut=10000;
    float minv = array_min(test_mem, n);
    float maxv = array_max(test_mem, n);
    float std = 0, std_old, mean;

    while (ct < 10)
    {
        ct++;
        std_old = std;
        mean = array_mean(test_mem, n, low_cut, high_cut);
        std = array_std(test_mem, n, mean, low_cut, high_cut);
        printf("mean = %2.8f std = %2.8f; min = %2.8f max = %2.8f\n", mean, std, minv, maxv);

        high_cut = maxv > mean + 2*std ? mean + 2*std : maxv;
        low_cut = minv < mean - 2*std ? mean - 2*std : minv;
        maxv = high_cut;
        minv = low_cut;

        if (fabs(std - std_old) / std < 0.05)
            break;
    }

    for (unsigned i = 0; i < requisition->dims[0] * requisition->dims[1]; i++) 
    {
        out_mem[i] = sigmoid(in_mem[i], mean, std, 0.3);
    }

    g_free(test_mem);

    return TRUE;
}

static void
ufo_piv_contrast_task_set_property (GObject *object,
                              guint property_id,
                              const GValue *value,
                              GParamSpec *pspec)
{
    UfoPivContrastTaskPrivate *priv = UFO_PIV_CONTRAST_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_TEST:
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_piv_contrast_task_get_property (GObject *object,
                              guint property_id,
                              GValue *value,
                              GParamSpec *pspec)
{
    UfoPivContrastTaskPrivate *priv = UFO_PIV_CONTRAST_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_TEST:
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_piv_contrast_task_finalize (GObject *object)
{
    G_OBJECT_CLASS (ufo_piv_contrast_task_parent_class)->finalize (object);
}

static void
ufo_task_interface_init (UfoTaskIface *iface)
{
    iface->setup = ufo_piv_contrast_task_setup;
    iface->get_num_inputs = ufo_piv_contrast_task_get_num_inputs;
    iface->get_num_dimensions = ufo_piv_contrast_task_get_num_dimensions;
    iface->get_mode = ufo_piv_contrast_task_get_mode;
    iface->get_requisition = ufo_piv_contrast_task_get_requisition;
    iface->process = ufo_piv_contrast_task_process;
}

static void
ufo_piv_contrast_task_class_init (UfoPivContrastTaskClass *klass)
{
    GObjectClass *oclass = G_OBJECT_CLASS (klass);

    oclass->set_property = ufo_piv_contrast_task_set_property;
    oclass->get_property = ufo_piv_contrast_task_get_property;
    oclass->finalize = ufo_piv_contrast_task_finalize;

    properties[PROP_TEST] =
        g_param_spec_string ("test",
            "Test property nick",
            "Test property description blurb",
            "",
            G_PARAM_READWRITE);

    for (guint i = PROP_0 + 1; i < N_PROPERTIES; i++)
        g_object_class_install_property (oclass, i, properties[i]);

    g_type_class_add_private (oclass, sizeof(UfoPivContrastTaskPrivate));
}

static void
ufo_piv_contrast_task_init(UfoPivContrastTask *self)
{
    self->priv = UFO_PIV_CONTRAST_TASK_GET_PRIVATE(self);
}
