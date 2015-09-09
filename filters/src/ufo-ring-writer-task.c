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

#include <stdio.h>
#include "ufo-ring-writer-task.h"
#include "ufo-ring-coordinates.h"


struct _UfoRingWriterTaskPrivate {
    gint foo;
};

static void ufo_task_interface_init (UfoTaskIface *iface);

G_DEFINE_TYPE_WITH_CODE (UfoRingWriterTask, ufo_ring_writer_task, UFO_TYPE_TASK_NODE,
                         G_IMPLEMENT_INTERFACE (UFO_TYPE_TASK,
                                                ufo_task_interface_init))

#define UFO_RING_WRITER_TASK_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE((obj), UFO_TYPE_RING_WRITER_TASK, UfoRingWriterTaskPrivate))

enum {
    PROP_0,
    PROP_TEST,
    N_PROPERTIES
};

static GParamSpec *properties[N_PROPERTIES] = { NULL, };

UfoNode *
ufo_ring_writer_task_new (void)
{
    return UFO_NODE (g_object_new (UFO_TYPE_RING_WRITER_TASK, NULL));
}

static void
ufo_ring_writer_task_setup (UfoTask *task,
                       UfoResources *resources,
                       GError **error)
{
}

static void
ufo_ring_writer_task_get_requisition (UfoTask *task,
                                 UfoBuffer **inputs,
                                 UfoRequisition *requisition)
{
    requisition->n_dims = 0;
}

static guint
ufo_ring_writer_task_get_num_inputs (UfoTask *task)
{
    return 1;
}

static guint
ufo_ring_writer_task_get_num_dimensions (UfoTask *task,
                                             guint input)
{
    return 1;
}

static UfoTaskMode
ufo_ring_writer_task_get_mode (UfoTask *task)
{
    return UFO_TASK_MODE_SINK | UFO_TASK_MODE_CPU;
}

static gboolean
ufo_ring_writer_task_process (UfoTask *task,
                         UfoBuffer **inputs,
                         UfoBuffer *output,
                         UfoRequisition *requisition)
{
    gfloat *in_mem = ufo_buffer_get_host_array (inputs[0], NULL);
    UfoRingCoordinate *rings = (UfoRingCoordinate*) (&in_mem[1]);
    unsigned num = in_mem[0]; 

    printf("#################################\n");
    printf("RingWriter: number of rings %u\n", num);
    for (unsigned  i = 0; i < num; i++) {
        printf("%8.0f %8.0f %8.0f %10.2f %10.2f\n",
                rings[i].x,
                rings[i].y,
                rings[i].r,
                rings[i].intensity,
                rings[i].contrast );
    }

    return TRUE;
}

static void
ufo_ring_writer_task_set_property (GObject *object,
                              guint property_id,
                              const GValue *value,
                              GParamSpec *pspec)
{
    UfoRingWriterTaskPrivate *priv = UFO_RING_WRITER_TASK_GET_PRIVATE (object);
    (void) priv;

    switch (property_id) {
        case PROP_TEST:
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_ring_writer_task_get_property (GObject *object,
                              guint property_id,
                              GValue *value,
                              GParamSpec *pspec)
{
    UfoRingWriterTaskPrivate *priv = UFO_RING_WRITER_TASK_GET_PRIVATE (object);
    (void) priv;

    switch (property_id) {
        case PROP_TEST:
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_ring_writer_task_finalize (GObject *object)
{
    G_OBJECT_CLASS (ufo_ring_writer_task_parent_class)->finalize (object);
}

static void
ufo_task_interface_init (UfoTaskIface *iface)
{
    iface->setup = ufo_ring_writer_task_setup;
    iface->get_num_inputs = ufo_ring_writer_task_get_num_inputs;
    iface->get_num_dimensions = ufo_ring_writer_task_get_num_dimensions;
    iface->get_mode = ufo_ring_writer_task_get_mode;
    iface->get_requisition = ufo_ring_writer_task_get_requisition;
    iface->process = ufo_ring_writer_task_process;
}

static void
ufo_ring_writer_task_class_init (UfoRingWriterTaskClass *klass)
{
    GObjectClass *oclass = G_OBJECT_CLASS (klass);

    oclass->set_property = ufo_ring_writer_task_set_property;
    oclass->get_property = ufo_ring_writer_task_get_property;
    oclass->finalize = ufo_ring_writer_task_finalize;

    properties[PROP_TEST] =
        g_param_spec_string ("test",
            "Test property nick",
            "Test property description blurb",
            "",
            G_PARAM_READWRITE);

    for (guint i = PROP_0 + 1; i < N_PROPERTIES; i++)
        g_object_class_install_property (oclass, i, properties[i]);

    g_type_class_add_private (oclass, sizeof(UfoRingWriterTaskPrivate));
}

static void
ufo_ring_writer_task_init(UfoRingWriterTask *self)
{
    self->priv = UFO_RING_WRITER_TASK_GET_PRIVATE(self);
}
