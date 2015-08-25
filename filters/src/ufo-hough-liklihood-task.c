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

#ifdef __APPLE__
#include <OpenCL/cl.h>
#else
#include <CL/cl.h>
#endif

#include "ufo-hough-liklihood-task.h"
#include <glib/gprintf.h>

struct _UfoHoughLiklihoodTaskPrivate {
    gint masksize;
    gfloat maskinnersize;
    cl_kernel kernel;
    cl_mem mask_mem;
};

static void ufo_task_interface_init (UfoTaskIface *iface);

G_DEFINE_TYPE_WITH_CODE (UfoHoughLiklihoodTask, ufo_hough_liklihood_task, UFO_TYPE_TASK_NODE,
                         G_IMPLEMENT_INTERFACE (UFO_TYPE_TASK,
                                                ufo_task_interface_init))

#define UFO_HOUGH_LIKLIHOOD_TASK_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE((obj), UFO_TYPE_HOUGH_LIKLIHOOD_TASK, UfoHoughLiklihoodTaskPrivate))

enum {
    PROP_0,
    PROP_MASKSIZE,
    PROP_MASKINNERSIZE,
    N_PROPERTIES
};

static GParamSpec *properties[N_PROPERTIES] = { NULL, };

UfoNode *
ufo_hough_liklihood_task_new (void)
{
    return UFO_NODE (g_object_new (UFO_TYPE_HOUGH_LIKLIHOOD_TASK, NULL));
}

static void
ufo_hough_liklihood_task_setup (UfoTask *task,
                       UfoResources *resources,
                       GError **error)
{
    UfoHoughLiklihoodTaskPrivate *priv;
    int i, j, i0, j0;
    int *mask;

    priv = UFO_HOUGH_LIKLIHOOD_TASK_GET_PRIVATE (task);

    mask = g_malloc0 (priv->masksize * priv->masksize * sizeof (int));
    for (i = 0, i0 = - (priv->masksize - 1) / 2; i < priv->masksize; i++, i0++)
        for (j = 0, j0 = - (priv->masksize - 1) / 2; j < priv->masksize; j++, j0++)
            if ((i0*i0 + j0*j0) >= priv->maskinnersize * priv->maskinnersize)
                mask[i + j*priv->masksize] = 1;

    // debug mask
    int *mask0 = mask;
    for (i = 0; i < priv->masksize; i++)
    {
        for (j = 0; j < priv->masksize; j++, mask0++)
            g_printf ("%d, ", *mask0);
        g_printf("\n");
    }
}

static void
ufo_hough_liklihood_task_get_requisition (UfoTask *task,
                                 UfoBuffer **inputs,
                                 UfoRequisition *requisition)
{
    ufo_buffer_get_requisition (inputs[0], requisition);
}

static guint
ufo_hough_liklihood_task_get_num_inputs (UfoTask *task)
{
    return 1;
}

static guint
ufo_hough_liklihood_task_get_num_dimensions (UfoTask *task,
                                             guint input)
{
    return 2;
}

static UfoTaskMode
ufo_hough_liklihood_task_get_mode (UfoTask *task)
{
    return UFO_TASK_MODE_PROCESSOR;
}

static gboolean
ufo_hough_liklihood_task_process (UfoTask *task,
                         UfoBuffer **inputs,
                         UfoBuffer *output,
                         UfoRequisition *requisition)
{
    ufo_buffer_copy(inputs[0], output);
    return TRUE;
}

static void
ufo_hough_liklihood_task_set_property (GObject *object,
                              guint property_id,
                              const GValue *value,
                              GParamSpec *pspec)
{
    UfoHoughLiklihoodTaskPrivate *priv = UFO_HOUGH_LIKLIHOOD_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_MASKSIZE:
            priv->masksize = g_value_get_int (value);
            if (priv->masksize % 2 != 1)
            {
                g_warning ("masksize (%d) must be odd number", priv->masksize);
                priv->masksize -= 1;
            }

            break;
        case PROP_MASKINNERSIZE:
            priv->maskinnersize = g_value_get_float (value);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_hough_liklihood_task_get_property (GObject *object,
                              guint property_id,
                              GValue *value,
                              GParamSpec *pspec)
{
    UfoHoughLiklihoodTaskPrivate *priv = UFO_HOUGH_LIKLIHOOD_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_MASKSIZE:
            g_value_set_int (value, priv->masksize);
            break;
        case PROP_MASKINNERSIZE:
            g_value_set_float (value, priv->maskinnersize);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_hough_liklihood_task_finalize (GObject *object)
{
    G_OBJECT_CLASS (ufo_hough_liklihood_task_parent_class)->finalize (object);
}

static void
ufo_task_interface_init (UfoTaskIface *iface)
{
    iface->setup = ufo_hough_liklihood_task_setup;
    iface->get_num_inputs = ufo_hough_liklihood_task_get_num_inputs;
    iface->get_num_dimensions = ufo_hough_liklihood_task_get_num_dimensions;
    iface->get_mode = ufo_hough_liklihood_task_get_mode;
    iface->get_requisition = ufo_hough_liklihood_task_get_requisition;
    iface->process = ufo_hough_liklihood_task_process;
}

static void
ufo_hough_liklihood_task_class_init (UfoHoughLiklihoodTaskClass *klass)
{
    GObjectClass *oclass = G_OBJECT_CLASS (klass);

    oclass->set_property = ufo_hough_liklihood_task_set_property;
    oclass->get_property = ufo_hough_liklihood_task_get_property;
    oclass->finalize = ufo_hough_liklihood_task_finalize;

    properties[PROP_MASKSIZE] =
        g_param_spec_int ("masksize",
            "Mask size",
            "Mask size",
            3, 21, 9,
            G_PARAM_READWRITE);

    properties[PROP_MASKINNERSIZE] =
        g_param_spec_float ("maskinnersize",
            "Mask inner size",
            "Mask inner size",
            1.f, 10.f, 1.f,
            G_PARAM_READWRITE);

    for (guint i = PROP_0 + 1; i < N_PROPERTIES; i++)
        g_object_class_install_property (oclass, i, properties[i]);

    g_type_class_add_private (oclass, sizeof(UfoHoughLiklihoodTaskPrivate));
}

static void
ufo_hough_liklihood_task_init(UfoHoughLiklihoodTask *self)
{
    self->priv = UFO_HOUGH_LIKLIHOOD_TASK_GET_PRIVATE(self);
    self->priv->masksize = 9;
    self->priv->maskinnersize = 1.0;
}
