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
#include <string.h>
#include <gsl/gsl_multifit_nlin.h>

#include "ufo-azimuthal-test-task.h"
#include "ufo-ring-coordinates.h"


struct _UfoAzimuthalTestTaskPrivate {
    guint radii_range;
    guint displacement;
    guint scale;
};

static void ufo_task_interface_init (UfoTaskIface *iface);

G_DEFINE_TYPE_WITH_CODE (UfoAzimuthalTestTask, ufo_azimuthal_test_task, UFO_TYPE_TASK_NODE,
                         G_IMPLEMENT_INTERFACE (UFO_TYPE_TASK,
                                                ufo_task_interface_init))

#define UFO_AZIMUTHAL_TEST_TASK_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE((obj), UFO_TYPE_AZIMUTHAL_TEST_TASK, UfoAzimuthalTestTaskPrivate))

enum {
    PROP_0,
    PROP_SCALE,
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
        int center_x, int center_y, int img_width, int img_height)
{
    int l = center_x - rad;
    int r = center_x + rad;
    int t = center_y - rad;
    int b = center_y + rad;
    *left = max (l, 0);
    *right = min (r, img_width - 1);
    *top = max (t, 0);
    *bot = min (b, img_height - 1);
}

static void
compute_histogram(float *histogram, float *h, float *img, int center_x, int center_y,
                        int min_r, int max_r, int img_width, int img_height)
{
    int x0, x1, y0, y1;
    int r,i,j,ii,jj,idx;

    get_coords(&x0, &x1, &y0, &y1, max_r, center_x, center_y, img_width, img_height);

    for (i = x0; i < x1; i++) for (j = y0; j < y1; j++) {
        idx = i + j * img_width;
        ii = i - center_x;
        jj = j - center_y;
        r = (int) roundf(sqrt(ii*ii+jj*jj));

        if (r >= min_r && r <= max_r) {
            if (img[idx] > 0.0f) {
                histogram[r - min_r] +=  img[idx];
                h[r - min_r] += 1;
            }
        }
    }

    for (r = 0; r < max_r - min_r + 1; r++)
        if (h[r] > 0) histogram[r] /= h[r];
}

static void
search_peaks(float *data, float *h, int wlen)
{
    int peak, i, j, k=0;
    for (i = 0; i < MAX_HIST_LEN - wlen - 1; i++) {
        peak = 0;
        for (j = i; j < i + wlen - 1; j++)
            if (data[j] >= data[j+1]) {
                peak = j;
                break;
            }
        for (; j < i + wlen - 1; j++)
            if (data[j] <= data[j+1]) break;
        if (peak != i + wlen/2 || j != i + wlen - 1 ||
                data[j] == 0.0f || data[i] == 0.0f) continue;
        h[k++] = peak;
    }
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


G_LOCK_DEFINE(binary_pic);

typedef struct _gaussian_thread_data{
    int tid;
   
    UfoAzimuthalTestTaskPrivate *priv;
    UfoRingCoordinate* ring;
   
    float* image;   // input image
    short* binary_pic; //Matrix of done pixels
    int img_width;
    int img_height;

    int tmp_S;
    UfoRingCoordinate* winner;
     
    GMutex* mutex;
} gaussian_thread_data;

#define HIST_MAX_LEN 32

static void gaussian_thread(gpointer data, gpointer user_data)
{
    int status;
    float histogram[HIST_MAX_LEN];
    float h[HIST_MAX_LEN];

    //Thread copying
    gaussian_thread_data *parm = (gaussian_thread_data*) data;

    float *image = parm->image;
    int img_width = parm->img_width;
    int img_height = parm->img_height;
    /*short* binary_pic = parm->binary_pic;*/
    UfoRingCoordinate* ring =  parm->ring;
    unsigned radii_range = parm->priv->radii_range;
    int displacement = parm->priv->displacement;

    // decide range of data to be considered in the fitting procedure
    // Since we aim at outer rings, keep the search range on the inner side strict,
    // and relax outer search range. This will help increase the probablility for
    // finding the peak position of the outer ring.
    int min_r = ring->r - radii_range;      
    int max_r = ring->r + radii_range + 6;  
    min_r = (min_r < 1) ? 1 : min_r;

    // initialize Gaussian fitting solver
    int nd = max_r - min_r + 1;
    int np = 3;

    const gsl_multifit_fdfsolver_type *T;
    gsl_multifit_fdfsolver *s;
    gsl_multifit_function_fdf f;
    gsl_vector_view view;
    gsl_matrix *covar;

    f.f = &gaussian_f;
    f.df = &gaussian_df;
    f.fdf = &gaussian_fdf;
    f.n = nd;
    f.p = np;

    T = gsl_multifit_fdfsolver_lmsder;
    s = gsl_multifit_fdfsolver_alloc(T, nd, np);
    covar = gsl_matrix_alloc (np, np);

    // loop through neighbour pixels and fit azimuthal histogram
    float ratio_max = 0.0f;
    for (int j = - displacement; j < displacement + 1; j++) {
        for (int k = - displacement; k < displacement + 1; k++) {
            g_message("\n");

            memset (histogram, 0, HIST_MAX_LEN * sizeof(*h));
            memset (h, 0, HIST_MAX_LEN * sizeof(*h));

            int rr;
            int peak_pos, peak_r;
            int center_x = ring->x + k;
            int center_y = ring->y + j;

            for(int r = min_r; r <= max_r; r++)
                histogram[r - min_r] = compute_intensity(image, r, 
                        center_x, center_y, img_width, img_height, radii_range);

            // smoothing histogram
            for (int r = 1; r < max_r - min_r; r++)
                h[r] = 0.5 * histogram[r] + 0.25 * (histogram[r+1] + histogram[r-1]);
            /*for (int r = 0; r < max_r - min_r + 1; r++)*/
                /*histogram[r] = h[r];*/

            memcpy(histogram, h, HIST_MAX_LEN * sizeof(*h));
            memset(h, 0, HIST_MAX_LEN * sizeof(*h));

            peak_pos = find_peak(histogram, max_r-min_r+1);
            peak_r = min_r + peak_pos;

            g_message("(%3d, %3d): r0 = %d, min_r = %d, max_r = %d, peak_r = %d, peak_pos = %d", 
                    (int)ring->x + k, (int)ring->y + j, 
                    (int)ring->r, min_r, max_r, peak_r, peak_pos);
            g_message(                                                          
                "histogram\
                \n\t\t%8.2f, %8.2f, %8.2f, %8.2f, %8.2f,\
                \n\t\t%8.2f, %8.2f, %8.2f, %8.2f, %8.2f,\
                \n\t\t%8.2f, %8.2f, %8.2f, %8.2f, %8.2f,\
                \n\t\t%8.2f, %8.2f, %8.2f, %8.2f, %8.2f,\
                \n\t\t%8.2f, %8.2f, %8.2f, %8.2f, %8.2f,\
                \n\t\t%8.2f, %8.2f, %8.2f, %8.2f, %8.2f,\
                \n\t\t%8.2f, %8.2f",
                histogram[0], histogram[1], histogram[2], histogram[3], histogram[4],
                histogram[5], histogram[6], histogram[7], histogram[8], histogram[9],
                histogram[10], histogram[11], histogram[12], histogram[13], histogram[14],
                histogram[15], histogram[16], histogram[17], histogram[18], histogram[19],
                histogram[20], histogram[21], histogram[22], histogram[23], histogram[24],
                histogram[25], histogram[26], histogram[27], histogram[28], histogram[29],
                histogram[30], histogram[31]);

            if (peak_pos <= 2 || peak_pos >= max_r - min_r - 1) continue;

            rr = 0;
            for (int r = peak_pos - 2; r < peak_pos + 3; r++, rr++) {
                h[rr] = histogram[r];
            }

            struct fitting_data d = {5, h};
            f.params = &d;

            // initial values for fitting parameter
            double x_init[] = {h[2], 2, 2};
            view = gsl_vector_view_array(x_init, 3);

            gsl_multifit_fdfsolver_set(s, &f, &view.vector);

            int iter = 0;
            do{
                iter++;
                status = gsl_multifit_fdfsolver_iterate(s);
                if(status) break;
                status = gsl_multifit_test_delta(s->dx, s->x, 1e-4, 1e-4);
            } while (status == GSL_CONTINUE && iter < 50);

            gsl_multifit_covar (s->J, 0.0, covar);

#define FIT(i) gsl_vector_get(s->x, i)
#define ERR(i) sqrt(gsl_matrix_get(covar,i,i))
                
            float parm_A = FIT(0);
            float parm_mu = FIT(1);
            float parm_sig = FIT(2);
            float err_A = ERR(0);
            float err_mu = ERR(1);
            float err_sig = ERR(2);
            float ratio  = fabs(parm_A/parm_sig);

            if (ratio > ratio_max) {
                ratio_max = ratio;
                parm->winner->x = (int) ring->x + k;
                parm->winner->y = (int) ring->y + j;
                parm->winner->r = peak_r + 2 - parm_mu;
                parm->winner->contrast = ring->contrast;
                /*if (parm_mu > 0.0f && parm_mu < 5.0f && parm_sig < 8.0f) {*/
                if (parm_mu > 0.0f && err_sig < 0.9f * parm_sig) {
                    parm->winner->intensity = ratio;
                } else {
                    parm->winner->intensity = -ratio;
                }
            }

            

            g_message("h = %.5f, %.5f, %.5f, %.5f, %.5f, ", h[0], h[1], h[2], h[3], h[4]);
            g_message( "A = %.5f (%.5f), sig = %.5f (%.5f), mu = %.5f (%.5f), A/sig = %.5f", 
                parm_A, err_A, parm_sig, err_sig, parm_mu, err_mu, ratio);
        }
    }
}

#define NUM_MAX_THREAD 1
static gboolean
ufo_azimuthal_test_task_process (UfoTask *task,
                         UfoBuffer **inputs,
                         UfoBuffer *output,
                         UfoRequisition *requisition)
{
    UfoAzimuthalTestTaskPrivate *priv;
    UfoRequisition req;

    priv = UFO_AZIMUTHAL_TEST_TASK_GET_PRIVATE (task);
    float *image = ufo_buffer_get_host_array (inputs[0], NULL);
    float *cand_stream = ufo_buffer_get_host_array (inputs[1], NULL);
    guint num_cand = (guint) *cand_stream;
    guint scale = (guint) cand_stream[1];
    UfoRingCoordinate *cand = (UfoRingCoordinate*) &cand_stream[2];

    ufo_buffer_get_requisition(inputs[0], &req);
    int img_width = req.dims[0];
    int img_height = req.dims[1];

    if (scale == 2)
        for (unsigned i = 0; i < num_cand; i++) {
            cand[i].x *= priv->scale;
            cand[i].y *= priv->scale;
            cand[i].r *= priv->scale;
        }

    /*short* binary_pic = g_malloc0(sizeof(short) * img_width *img_height);*/
    gaussian_thread_data thread_data[num_cand];
    UfoRingCoordinate results[num_cand];

    GError *err;
    GThreadPool *thread_pool = NULL;
    thread_pool = g_thread_pool_new((GFunc) gaussian_thread, NULL, NUM_MAX_THREAD, TRUE,&err);

    /*static GMutex mutex = G_STATIC_MUTEX_INIT;*/

    for (unsigned i = 0; i < num_cand; i++) {
        thread_data[i].tid = i;
        thread_data[i].priv = priv;
        thread_data[i].ring = &cand[i];
        thread_data[i].image = image;
        /*thread_data[i].binary_pic = binary_pic;*/
        thread_data[i].img_width = img_width;
        thread_data[i].img_height = img_height;
        thread_data[i].winner = &results[i];
        /*thread_data[i].mutex = &mutex;*/
        
        g_thread_pool_push(thread_pool, &thread_data[i],&err); 
    }

    g_thread_pool_free(thread_pool, FALSE, TRUE);

    float *res = ufo_buffer_get_host_array(output, NULL);

    UfoRingCoordinate *rings = (UfoRingCoordinate*) &res[1];

    int num = 0;
    for(unsigned i=0; i < num_cand;i++) {
        if (results[i].intensity > 0.0f) {
            rings[num] = results[i];
            num++;
        }
    }
    res[0] = num;
    
    /*req.n_dims = 1;*/
    /*req.dims[0] = 1 + num * sizeof(UfoRingCoordinate) / sizeof(float);*/
    /*ufo_buffer_resize(output, &req);*/

    /*g_free(binary_pic);*/
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
        case PROP_SCALE:
            priv->scale = g_value_get_uint(value);
            priv->displacement = priv->scale;
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
        case PROP_SCALE:
            g_value_set_uint (value, priv->scale);
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

    properties[PROP_SCALE] =
        g_param_spec_uint ("scale",
               "Rescale factor", "",
               1, 2, 1,
               G_PARAM_READWRITE);

    for (guint i = PROP_0 + 1; i < N_PROPERTIES; i++)
        g_object_class_install_property (oclass, i, properties[i]);

    g_type_class_add_private (oclass, sizeof(UfoAzimuthalTestTaskPrivate));
}

static void
ufo_azimuthal_test_task_init(UfoAzimuthalTestTask *self)
{
    self->priv = UFO_AZIMUTHAL_TEST_TASK_GET_PRIVATE(self);
    self->priv->radii_range = 10;
    self->priv->displacement = 1;
    self->priv->scale = 1;
}
