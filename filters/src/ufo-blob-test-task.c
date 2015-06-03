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

#include <stdio.h>
#include <math.h>
#include <string.h>
#include "ufo-blob-test-task.h"
#include "ufo-ring-coordinates.h"

struct _UfoBlobTestTaskPrivate {
    guint dimx;
    guint dimy;
    guint num_img;
    guint max_detection;
    unsigned ring_start;
    unsigned ring_end;
    unsigned ring_step;
    UfoBuffer *tmp_buffer;
    cl_context context;
};

static void ufo_task_interface_init (UfoTaskIface *iface);
static gfloat find_max(gfloat *, guint, guint, guint, guint);
static gfloat snr_max(gfloat *, gint, gint, gint, gint, gint, gint);

G_DEFINE_TYPE_WITH_CODE (UfoBlobTestTask, ufo_blob_test_task, UFO_TYPE_TASK_NODE,
                         G_IMPLEMENT_INTERFACE (UFO_TYPE_TASK,
                                                ufo_task_interface_init))

#define UFO_BLOB_TEST_TASK_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE((obj), UFO_TYPE_BLOB_TEST_TASK, UfoBlobTestTaskPrivate))

enum {
    PROP_0,
    PROP_MAX_DETECTION,
    PROP_RING_START,
    PROP_RING_STEP,
    PROP_RING_END,
    N_PROPERTIES
};

static GParamSpec *properties[N_PROPERTIES] = { NULL, };

UfoNode *
ufo_blob_test_task_new (void)
{
    return UFO_NODE (g_object_new (UFO_TYPE_BLOB_TEST_TASK, NULL));
}

static void
ufo_blob_test_task_setup (UfoTask *task,
                       UfoResources *resources,
                       GError **error)
{
    UfoBlobTestTaskPrivate *priv = UFO_BLOB_TEST_TASK_GET_PRIVATE (task);
    priv->context = ufo_resources_get_context (resources);
}

static void
ufo_blob_test_task_get_requisition (UfoTask *task,
                                 UfoBuffer **inputs,
                                 UfoRequisition *requisition)
{
    UfoBlobTestTaskPrivate *priv = UFO_BLOB_TEST_TASK_GET_PRIVATE (task);
    UfoRequisition req_in, req_tmp; 

    ufo_buffer_get_requisition (inputs[0], &req_in);
    priv->dimx = req_in.dims[0];
    priv->dimy = req_in.dims[1];
    priv->num_img = req_in.dims[2];

    requisition->n_dims = 2;
    requisition->dims[0] = 3*priv->max_detection + 1;
    requisition->dims[1] = req_in.dims[2];

    req_tmp = req_in;
    req_tmp.n_dims = 2;
    priv->tmp_buffer = ufo_buffer_new(&req_tmp, priv->context);
}

static guint
ufo_blob_test_task_get_num_inputs (UfoTask *task)
{
    return 1;
}

static guint
ufo_blob_test_task_get_num_dimensions (UfoTask *task,
                                             guint input)
{
    return 3;
}

static UfoTaskMode
ufo_blob_test_task_get_mode (UfoTask *task)
{
    return UFO_TASK_MODE_PROCESSOR | UFO_TASK_MODE_CPU;
}

static gboolean
ufo_blob_test_task_process (UfoTask *task,
                         UfoBuffer **inputs,
                         UfoBuffer *output,
                         UfoRequisition *requisition)
{
    UfoBlobTestTaskPrivate *priv = UFO_BLOB_TEST_TASK_GET_PRIVATE (task);

    gfloat *in_mem = ufo_buffer_get_host_array(inputs[0], NULL);
    gfloat *out_mem = ufo_buffer_get_host_array(output, NULL);
    gfloat *tmp_mem = ufo_buffer_get_host_array(priv->tmp_buffer, NULL);
    gsize img_size = priv->dimx * priv->dimy;

    for (guint ct_img = 0; ct_img < priv->num_img; ct_img++) {
        // initialize temp memory
        for (gsize i = 0; i < img_size; i++) {
            tmp_mem[i] = 0.0f;
        }

        // shift image pointer
        gfloat *img_mem = in_mem + img_size * ct_img;

        // find global maxima
        float glb_max = 0.0f;
        for (gsize i = 0; i < img_size; i++) {
            glb_max = (img_mem[i] > glb_max) ? img_mem[i] : glb_max;
        }

        // find local maxima and save them in temp buffer
        float threshold = 0.4f;
        int ct = 0;
        for (gsize ix = 1; ix < priv->dimx - 1; ix++)
        for (gsize iy = 1; iy < priv->dimy - 1; iy++) {
            gsize i = ix + priv->dimx * iy;
            if (( img_mem[i] > threshold * glb_max ) &&
                ( img_mem[i] > find_max(img_mem, ix, iy, priv->dimx, priv->dimy) ))  {
                tmp_mem[i] = 1.0f;
                ct++;
            }
        }

        // blob test
        ct = 0;
        for (gsize ix = 1; ix < priv->dimx - 1; ix++)
        for (gsize iy = 1; iy < priv->dimy - 1; iy++) {
            gsize i = ix + priv->dimx * iy;

            if (ct >= (int) priv->max_detection) {
                g_warning ("BlobTestTask: Maximum detection reached");
                break;
            }

            if (tmp_mem[i] > 0.5f) {
                float alpha = snr_max(img_mem, ix, iy, 2, 3, priv->dimx, priv->dimy);

                if (alpha > 2.0f) {
                    // g_warning ("BlobTestTask: detected: %4lu %4lu %f", ix, iy, alpha);
                    out_mem[3*ct+1] = (gfloat) ix;
                    out_mem[3*ct+2] = (gfloat) iy;
                    out_mem[3*ct+3] = alpha;
                    ct++;
                } else {
                    tmp_mem[i] = 0.0f;
                }
            }
        }
        out_mem[0] = ct;
    }

    return TRUE;

}

static void
ufo_blob_test_task_set_property (GObject *object,
                              guint property_id,
                              const GValue *value,
                              GParamSpec *pspec)
{
    UfoBlobTestTaskPrivate *priv = UFO_BLOB_TEST_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_MAX_DETECTION:
            priv->max_detection = g_value_get_uint(value);
            break;
        case PROP_RING_START:
            priv->ring_start = g_value_get_uint(value);
            break;
        case PROP_RING_STEP:
            priv->ring_step = g_value_get_uint(value);
            break;
        case PROP_RING_END:
            priv->ring_end = g_value_get_uint(value);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_blob_test_task_get_property (GObject *object,
                              guint property_id,
                              GValue *value,
                              GParamSpec *pspec)
{
    UfoBlobTestTaskPrivate *priv = UFO_BLOB_TEST_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_MAX_DETECTION:
            g_value_set_uint (value, priv->max_detection);
            break;
        case PROP_RING_START:
            g_value_set_uint (value, priv->ring_start);
            break;
        case PROP_RING_STEP:
            g_value_set_uint (value, priv->ring_step);
            break;
        case PROP_RING_END:
            g_value_set_uint (value, priv->ring_end);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_blob_test_task_finalize (GObject *object)
{
    G_OBJECT_CLASS (ufo_blob_test_task_parent_class)->finalize (object);
}

static void
ufo_task_interface_init (UfoTaskIface *iface)
{
    iface->setup = ufo_blob_test_task_setup;
    iface->get_num_inputs = ufo_blob_test_task_get_num_inputs;
    iface->get_num_dimensions = ufo_blob_test_task_get_num_dimensions;
    iface->get_mode = ufo_blob_test_task_get_mode;
    iface->get_requisition = ufo_blob_test_task_get_requisition;
    iface->process = ufo_blob_test_task_process;
}

static void
ufo_blob_test_task_class_init (UfoBlobTestTaskClass *klass)
{
    GObjectClass *oclass = G_OBJECT_CLASS (klass);

    oclass->set_property = ufo_blob_test_task_set_property;
    oclass->get_property = ufo_blob_test_task_get_property;
    oclass->finalize = ufo_blob_test_task_finalize;

    properties[PROP_MAX_DETECTION] =
        g_param_spec_uint ("max_detection",
                           "max detection per ring size",
                           "max number of detected rings per ring size",
                           1, G_MAXUINT, 100,
                           G_PARAM_READWRITE);
    properties[PROP_RING_START] =
        g_param_spec_uint ("ring_start",
                           "give starting radius size",
                           "give starting radius size",
                           1, G_MAXUINT, 5,
                           G_PARAM_READWRITE);

    properties[PROP_RING_STEP] =
        g_param_spec_uint ("ring_step",
                           "Gives ring step",
                           "Gives ring step",
                           1, G_MAXUINT, 2,
                           G_PARAM_READWRITE);

    properties[PROP_RING_END] =
        g_param_spec_uint ("ring_end",
                           "give ending radius size",
                           "give ending radius size",
                           1, G_MAXUINT, 5,
                           G_PARAM_READWRITE);

    for (guint i = PROP_0 + 1; i < N_PROPERTIES; i++)
        g_object_class_install_property (oclass, i, properties[i]);

    g_type_class_add_private (oclass, sizeof(UfoBlobTestTaskPrivate));
}

static void
ufo_blob_test_task_init(UfoBlobTestTask *self)
{
    self->priv = UFO_BLOB_TEST_TASK_GET_PRIVATE(self);
    self->priv->max_detection = 100;
    self->priv->ring_start = 5;
    self->priv->ring_end = 5;
    self->priv->ring_step = 2;
}

//////////////////////////////////////////////////////////////////////////////
// internal helper functions
//////////////////////////////////////////////////////////////////////////////
static gfloat array_mean(gfloat *arr, gint n) {
    gfloat res = 0.0f;
    for (gint i = 0; i < n; i++) res += arr[i];
    return res/n;
}

static gfloat array_sigma(gfloat *arr, gfloat mean, gint n) {
    gfloat res = 0.0f;
    for (gint i = 0; i < n; i++) res += ( arr[i] - mean ) * ( arr[i] - mean );
    return sqrt(res/(n-1));
}

/*
 *  @s: inner size
 *  @t: outer size
 */

static gfloat
snr(gfloat *img_ptr, gint idx, gint idy, gint s, gint t, gint dimx, gint dimy) {
    gint pos;
    gfloat sig[100];
    gfloat bak[400];
    gint mask[21][21];

    // inner size must be smaller than outer size
    // outer size must not be larger than 10
    if (s > t) return -1.0f;
    if (t > 5) return -1.0f;

    // when pixel is close to boundary, discard it
    if (idx - t - 2 < 0) return -1.0f;
    if (idy - t - 2 < 0) return -1.0f;
    if (idx + t + 2>= dimx) return -1.0f;
    if (idy + t + 2>= dimy) return -1.0f;

    // get signal pixels from inner region 
    gint ns = 0;
    for (gint ix = idx - s; ix < idx + s + 1; ix++)
    for (gint iy = idy - s; iy < idy + s + 1; iy++) {
        pos = ix + dimx * iy;
        sig[ns] = img_ptr[pos];
        ns++;
    }

    // get background pixels from outer region
    for (gint i = 0; i < 21; i++)
    for (gint j = 0; j < 21; j++) {
        mask[i][j] = 0;
    }

    gint mid = 10;
    for (gint i = mid-t-2; i < mid+t+3; i++)
    for (gint j = mid-t-2; j < mid+t+3; j++) {
        mask[i][j] = 1;
    }

    for (gint i = mid-t; i < mid+t+1; i++)
    for (gint j = mid-t; j < mid+t+1; j++) {
        mask[i][j] = 0;
    }

    for (gint i = 0; i < 21; i++)                                                                         
    for (gint j = 0; j < 21; j++) {                                                                        
        pos = (i + idx - mid) + (j + idy - mid) * dimx;
        mask[i][j] *= pos;
    }

    gint nb = 0;
    for (gint i = 0; i < 21; i++)                                                                         
    for (gint j = 0; j < 21; j++) {                                                                        
        if ( mask[i][j] != 0 ) {
            pos = mask[i][j];
            bak[nb] = img_ptr[pos];
            nb++;
        }
    }

    gfloat mu_s = array_mean(sig, ns);
    gfloat mu_b = array_mean(bak, nb);

    // gfloat sig_s = array_sigma(sig, mu_s, ns);
    gfloat sig_b = array_sigma(bak, mu_b, nb);

    // gfloat res = (mu_s - mu_b) / sqrt(nb*sig_s*sig_s + ns*sig_b*sig_b);
    gfloat res = (mu_s - mu_b) / sqrt(ns*sig_b*sig_b + ns*sig_b*sig_b/nb);

    // printf("\t%.2f\t%.4e, %.4e, %.4e, %.4e, %4d, %4d\n", res, mu_s-mu_b, mu_b, sig_s, sig_b, ns, nb);
    return res;
}

static gfloat
snr_max(gfloat *img_ptr, gint idx, gint idy, gint s, gint t, gint dimx, gint dimy) {
    gfloat res, snr_array[10] = {0};

    /*
    snr_array[0] = snr(img_ptr, idx, idy, 2, t, dimx, dimy);
    snr_array[1] = snr(img_ptr, idx - 1, idy, 2, t, dimx, dimy);
    snr_array[2] = snr(img_ptr, idx + 1, idy, 2, t, dimx, dimy);
    snr_array[3] = snr(img_ptr, idx, idy - 1, 2, t, dimx, dimy);
    snr_array[4] = snr(img_ptr, idx, idy + 1, 2, t, dimx, dimy);
    */

    snr_array[5] = snr(img_ptr, idx, idy, 1, t, dimx, dimy);
    snr_array[6] = snr(img_ptr, idx - 1, idy, 1, t, dimx, dimy);
    snr_array[7] = snr(img_ptr, idx + 1, idy, 1, t, dimx, dimy);
    snr_array[8] = snr(img_ptr, idx, idy - 1, 1, t, dimx, dimy);
    snr_array[9] = snr(img_ptr, idx, idy + 1, 1, t, dimx, dimy);

    res = snr_array[0];
    for (gint i = 1; i < 10; i++) {
        res = (res > snr_array[i]) ? res : snr_array[i];
    }

    return res;
}

static gfloat
find_max(gfloat *ptr, guint idxx, guint idxy, guint dimx, guint dimy) {
    gfloat a, b;

    b = ptr[idxx-1  + dimx * (idxy-1)];

    b = MAX(ptr[idxx + dimx * (idxy-1)], b);
    // b = (b > a) ? b : a;

    a = ptr[idxx+1 + dimx * (idxy-1)];
    b = (b > a) ? b : a;

    a = ptr[idxx-1 + dimx * idxy];
    b = (b > a) ? b : a;

    a = ptr[idxx+1 + dimx * idxy];
    b = (b > a) ? b : a;

    a = ptr[idxx-1  + dimx * (idxy+1)];
    b = (b > a) ? b : a;

    a = ptr[idxx + dimx * (idxy+1)];
    b = (b > a) ? b : a;

    a = ptr[idxx+1 + dimx * (idxy+1)];
    b = (b > a) ? b : a;

    return b;
}


