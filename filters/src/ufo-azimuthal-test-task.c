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

#include <math.h>
#include <gsl/gsl_multifit_nlin.h>

#include "ufo-azimuthal-test-task.h"
#include "ufo-ring-coordinates.h"


struct _UfoAzimuthalTestTaskPrivate {
    guint radii_range;
    guint displacement;
};

static void ufo_task_interface_init (UfoTaskIface *iface);

G_DEFINE_TYPE_WITH_CODE (UfoAzimuthalTestTask, ufo_azimuthal_test_task, UFO_TYPE_TASK_NODE,
                         G_IMPLEMENT_INTERFACE (UFO_TYPE_TASK,
                                                ufo_task_interface_init))

#define UFO_AZIMUTHAL_TEST_TASK_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE((obj), UFO_TYPE_AZIMUTHAL_TEST_TASK, UfoAzimuthalTestTaskPrivate))

enum {
    PROP_0,
    PROP_TEST,
    N_PROPERTIES
};

static GParamSpec *properties[N_PROPERTIES] = { NULL, };

UfoNode *
ufo_azimuthal_test_task_new (void)
{
    return UFO_NODE (g_object_new (UFO_TYPE_AZIMUTHAL_TEST_TASK, NULL));
}

static void
ufo_azimuthal_test_task_setup (UfoTask *task,
                       UfoResources *resources,
                       GError **error)
{

}

static void
ufo_azimuthal_test_task_get_requisition (UfoTask *task,
                                 UfoBuffer **inputs,
                                 UfoRequisition *requisition)
{
    ufo_buffer_get_requisition (inputs[1], requisition);
}

static guint
ufo_azimuthal_test_task_get_num_inputs (UfoTask *task)
{
    return 2;
}

static guint
ufo_azimuthal_test_task_get_num_dimensions (UfoTask *task,
                                             guint input)
{
    return (input == 0) ?  2 : 1;
}

static UfoTaskMode
ufo_azimuthal_test_task_get_mode (UfoTask *task)
{
    return UFO_TASK_MODE_PROCESSOR;
}

static int min (int l, int r)
{
    return (l > r) ? r : l;
}

static int max (int l, int r)
{
    return (l > r) ? l : r;
}

static void
get_coords(int *left, int *right, int *top, int *bot, int rad,
        UfoRequisition *req, UfoRingCoordinate *center)
{
    int l = (int) roundf (center->x - (float) rad);
    int r = (int) roundf (center->x + (float) rad);
    int t = (int) roundf (center->y - (float) rad);
    int b = (int) roundf (center->y + (float) rad);
    *left = max (l, 0);
    *right = min (r, (int) (req->dims[0]) - 1);
    // Bottom most point is req->dims[1]
    *top = max (t, 0);
    // Top most point is 0
    *bot = min (b, (int) (req->dims[1]) - 1);
}

static float
compute_intensity (UfoBuffer *ufo_image, UfoRingCoordinate *center, int r)
{
    float intensity = 0;
    UfoRequisition req;
    ufo_buffer_get_requisition(ufo_image, &req);
    float *image = ufo_buffer_get_host_array(ufo_image, NULL);
    int x_center = (int) roundf (center->x);
    int y_center = (int) roundf (center->y);
    int left, right, top, bot;
    get_coords(&left, &right, &top, &bot, r, &req, center);
    unsigned counter = 0;
    
    for (int y = top; y <= bot; ++y) {
        for (int x = left; x <= right; ++x) {
            int xx = (x - x_center) * (x - x_center);
            int yy = (y - y_center) * (y - y_center);
            /* Check if point is on ring */
            if (fabs (sqrtf ((float) (xx + yy)) - (float) r) < 0.5) {
                intensity += image[x + y * (int) req.dims[0]];
                ++counter;
            }
        }
    }

    /*return intensity;*/

    
    if(counter != 0)
        return intensity / (float) counter;
    else    
        return 0;
}

struct fitting_data {
    size_t n;
    float *y;
};

static int gaussian_f (const gsl_vector *x, void *data, gsl_vector *f)
{
    size_t n = ((struct fitting_data *) data)->n;
    float *y = ((struct fitting_data *) data)->y;

    float A = gsl_vector_get(x, 0);
    float mu = gsl_vector_get(x, 1);
    float sig = gsl_vector_get(x, 2);

    for (size_t i = 0; i < n; i++)
    {
        float Yi = A * exp ( - (i - mu) * (i - mu) / (2.0f * sig * sig));
        gsl_vector_set (f, i, Yi - y[i]);
    }

    return GSL_SUCCESS;
}

static int gaussian_df (const gsl_vector *x, void *data, gsl_matrix *J)
{
    size_t n = ((struct fitting_data *) data)->n;

    float A = gsl_vector_get(x, 0);
    float mu = gsl_vector_get(x, 1);
    float sig = gsl_vector_get(x, 2);

    for (size_t i = 0; i < n; i++)
    {
        double t = i;
        double e = exp ( - (t - mu)*(t - mu) / (2.0f*sig*sig) );
        gsl_matrix_set (J, i, 0, e);
        gsl_matrix_set (J, i, 1, A * e * (t-mu) / (sig*sig) );
        gsl_matrix_set (J, i, 2, A * e * (t-mu)*(t-mu) / (sig*sig*sig) );
    }
    return GSL_SUCCESS;
}

static int gaussian_fdf (const gsl_vector *x, void *data, gsl_vector *f, gsl_matrix *J)
{
    gaussian_f (x, data, f);
    gaussian_df (x, data, J);
    return GSL_SUCCESS;
}

static gboolean
ufo_azimuthal_test_task_process (UfoTask *task,
                         UfoBuffer **inputs,
                         UfoBuffer *output,
                         UfoRequisition *requisition)
{
    UfoAzimuthalTestTaskPrivate *priv = UFO_AZIMUTHAL_TEST_TASK_GET_PRIVATE (task);

    float *in_cpu = ufo_buffer_get_host_array (inputs[1], NULL);
    guint num_cand = (guint) in_cpu[0];
    UfoRingCoordinate *cand = (UfoRingCoordinate*) &in_cpu[1];

    const gsl_multifit_fdfsolver_type *T;
    gsl_multifit_fdfsolver *s;

    T = gsl_multifit_fdfsolver_lmsder;
    gsl_multifit_function_fdf f;
    int status;

    f.f = &gaussian_f;
    f.df = &gaussian_df;
    f.fdf = &gaussian_fdf;
    f.p = 3;

    for (unsigned i = 0; i < num_cand; i++) {
        int min_r = cand[i].r - priv->radii_range;
        int max_r = cand[i].r + priv->radii_range;
        min_r = (min_r < 1) ? 1 : min_r;

        g_message ("************");
        g_message("ring %d %d %d", (int)cand[i].x, (int)cand[i].y, (int)cand[i].r);

        float histogram[max_r - min_r + 1];

        double x_init[] = {10, cand[i].r, 2};
        gsl_vector_view x = gsl_vector_view_array (x_init, 3);
        s = gsl_multifit_fdfsolver_alloc (T, max_r - min_r + 1, 3);
        f.n = max_r - min_r + 1;

        /*for (int j = -priv->displacement; j < priv->displacement + 1; j++)*/
        /*for (int k = -priv->displacement; k < priv->displacement + 1; k++)*/
        for (int j = -2; j < 3; j++)
        for (int k = -2; k < 3; k++)
        {
            UfoRingCoordinate ring = {cand[i].x + j, cand[i].y + k, cand[i].r, 0.0, 0.0};
            for (int r = min_r; r <= max_r; ++r) {
                histogram[r-min_r] = compute_intensity(inputs[0], &ring, r);
            }

            struct fitting_data d = {max_r - min_r + 1, histogram};
            f.params = &d;
            gsl_multifit_fdfsolver_set(s, &f, &x.vector);
            int iter = 0;

            do {
                iter++;
                status = gsl_multifit_fdfsolver_iterate (s);
                if (status) break;

                status = gsl_multifit_test_delta (s->dx, s->x, 1e-4, 1e-4);
            } while (status == GSL_CONTINUE && iter < 50);

            g_message(
                "histogram = %.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f",
                histogram[0], histogram[1], histogram[2], histogram[3], histogram[4], 
                histogram[5], histogram[6], histogram[7], histogram[8], histogram[9]); 

            g_message ("iter = %d", iter);
            g_message ("min_r = %d", min_r);
            g_message ("A   = %.5f", gsl_vector_get(s->x, 0));
            g_message ("mu  = %.5f", gsl_vector_get(s->x, 1));
            g_message ("sig = %.5f", fabs(gsl_vector_get(s->x, 2)));
            g_message ("x = %d y = %d A/sig = %.5f", (int)ring.x, (int)ring.y, gsl_vector_get(s->x, 0) / fabs(gsl_vector_get(s->x, 2)));
        }
    }

    g_message ("process");
    return TRUE;
}

static void
ufo_azimuthal_test_task_set_property (GObject *object,
                              guint property_id,
                              const GValue *value,
                              GParamSpec *pspec)
{
    UfoAzimuthalTestTaskPrivate *priv = UFO_AZIMUTHAL_TEST_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_TEST:
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_azimuthal_test_task_get_property (GObject *object,
                              guint property_id,
                              GValue *value,
                              GParamSpec *pspec)
{
    UfoAzimuthalTestTaskPrivate *priv = UFO_AZIMUTHAL_TEST_TASK_GET_PRIVATE (object);

    switch (property_id) {
        case PROP_TEST:
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
            break;
    }
}

static void
ufo_azimuthal_test_task_finalize (GObject *object)
{
    G_OBJECT_CLASS (ufo_azimuthal_test_task_parent_class)->finalize (object);
}

static void
ufo_task_interface_init (UfoTaskIface *iface)
{
    iface->setup = ufo_azimuthal_test_task_setup;
    iface->get_num_inputs = ufo_azimuthal_test_task_get_num_inputs;
    iface->get_num_dimensions = ufo_azimuthal_test_task_get_num_dimensions;
    iface->get_mode = ufo_azimuthal_test_task_get_mode;
    iface->get_requisition = ufo_azimuthal_test_task_get_requisition;
    iface->process = ufo_azimuthal_test_task_process;
}

static void
ufo_azimuthal_test_task_class_init (UfoAzimuthalTestTaskClass *klass)
{
    GObjectClass *oclass = G_OBJECT_CLASS (klass);

    oclass->set_property = ufo_azimuthal_test_task_set_property;
    oclass->get_property = ufo_azimuthal_test_task_get_property;
    oclass->finalize = ufo_azimuthal_test_task_finalize;

    properties[PROP_TEST] =
        g_param_spec_string ("test",
            "Test property nick",
            "Test property description blurb",
            "",
            G_PARAM_READWRITE);

    for (guint i = PROP_0 + 1; i < N_PROPERTIES; i++)
        g_object_class_install_property (oclass, i, properties[i]);

    g_type_class_add_private (oclass, sizeof(UfoAzimuthalTestTaskPrivate));
}

static void
ufo_azimuthal_test_task_init(UfoAzimuthalTestTask *self)
{
    self->priv = UFO_AZIMUTHAL_TEST_TASK_GET_PRIVATE(self);
    self->priv->radii_range = 5;
    self->priv->displacement = 1;
}
