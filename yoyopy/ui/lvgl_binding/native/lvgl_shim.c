#include "lvgl.h"
#include "lvgl_shim.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define KEY_QUEUE_CAPACITY 32

typedef struct {
    int32_t key;
    int32_t pressed;
} yoyopy_key_event_t;

static int g_initialized = 0;
static lv_display_t * g_display = NULL;
static lv_indev_t * g_indev = NULL;
static lv_group_t * g_group = NULL;
static lv_color_t * g_draw_buf = NULL;
static uint32_t g_draw_buf_bytes = 0;
static yoyopy_lvgl_flush_cb_t g_flush_cb = NULL;
static void * g_flush_user_data = NULL;
static char g_last_error[256] = "";
static yoyopy_key_event_t g_key_queue[KEY_QUEUE_CAPACITY];
static int g_key_head = 0;
static int g_key_tail = 0;
static int g_key_count = 0;

static void yoyopy_set_error(const char * message) {
    if(message == NULL) {
        g_last_error[0] = '\0';
        return;
    }

    strncpy(g_last_error, message, sizeof(g_last_error) - 1);
    g_last_error[sizeof(g_last_error) - 1] = '\0';
}

static int yoyopy_translate_key(int32_t key) {
    switch(key) {
        case YOYOPY_LVGL_KEY_RIGHT:
            return LV_KEY_RIGHT;
        case YOYOPY_LVGL_KEY_ENTER:
            return LV_KEY_ENTER;
        case YOYOPY_LVGL_KEY_ESC:
            return LV_KEY_ESC;
        default:
            return 0;
    }
}

static void yoyopy_flush_cb(lv_display_t * disp, const lv_area_t * area, uint8_t * px_map) {
    int32_t width = lv_area_get_width(area);
    int32_t height = lv_area_get_height(area);
    uint32_t byte_length = (uint32_t)(width * height * sizeof(lv_color_t));

    if(g_flush_cb != NULL) {
        g_flush_cb(
            area->x1,
            area->y1,
            width,
            height,
            (const unsigned char *)px_map,
            byte_length,
            g_flush_user_data
        );
    }

    lv_display_flush_ready(disp);
}

static void yoyopy_indev_read_cb(lv_indev_t * indev, lv_indev_data_t * data) {
    (void)indev;

    if(g_key_count == 0) {
        data->state = LV_INDEV_STATE_RELEASED;
        data->key = 0;
        data->continue_reading = 0;
        return;
    }

    yoyopy_key_event_t event = g_key_queue[g_key_head];
    g_key_head = (g_key_head + 1) % KEY_QUEUE_CAPACITY;
    g_key_count--;

    data->key = yoyopy_translate_key(event.key);
    data->state = event.pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
    data->continue_reading = g_key_count > 0 ? 1 : 0;
}

static void yoyopy_clear_group(void) {
    if(g_group != NULL) {
        lv_group_remove_all_objs(g_group);
    }
}

static lv_obj_t * yoyopy_create_card(lv_obj_t * screen, const char * title, const char * subtitle, lv_color_t accent) {
    lv_obj_t * panel = lv_obj_create(screen);
    lv_obj_set_size(panel, 200, 190);
    lv_obj_align(panel, LV_ALIGN_CENTER, 0, 8);
    lv_obj_set_style_radius(panel, 24, 0);
    lv_obj_set_style_border_width(panel, 2, 0);
    lv_obj_set_style_border_color(panel, accent, 0);
    lv_obj_set_style_bg_color(panel, lv_color_hex(0x222634), 0);
    lv_obj_set_style_bg_opa(panel, LV_OPA_COVER, 0);
    lv_obj_set_style_pad_all(panel, 16, 0);
    lv_obj_set_layout(panel, LV_LAYOUT_FLEX);
    lv_obj_set_flex_flow(panel, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(panel, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

    lv_obj_t * icon = lv_obj_create(panel);
    lv_obj_set_size(icon, 72, 72);
    lv_obj_set_style_radius(icon, 20, 0);
    lv_obj_set_style_bg_color(icon, accent, 0);
    lv_obj_set_style_bg_opa(icon, LV_OPA_20, 0);
    lv_obj_set_style_border_width(icon, 2, 0);
    lv_obj_set_style_border_color(icon, accent, 0);

    lv_obj_t * title_label = lv_label_create(panel);
    lv_label_set_text(title_label, title);
    lv_obj_set_style_text_font(title_label, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(title_label, lv_color_hex(0xF6F6F8), 0);

    lv_obj_t * subtitle_label = lv_label_create(panel);
    lv_label_set_text(subtitle_label, subtitle);
    lv_obj_set_style_text_font(subtitle_label, &lv_font_montserrat_16, 0);
    lv_obj_set_style_text_color(subtitle_label, accent, 0);

    return panel;
}

static void yoyopy_build_card_scene(void) {
    lv_obj_t * screen = lv_screen_active();
    lv_obj_clean(screen);
    yoyopy_clear_group();
    yoyopy_create_card(screen, "Listen", "LVGL card proof", lv_color_hex(0x98D94C));
}

static void yoyopy_build_list_scene(void) {
    lv_obj_t * screen = lv_screen_active();
    lv_obj_clean(screen);
    yoyopy_clear_group();

    lv_obj_t * list = lv_list_create(screen);
    lv_obj_set_size(list, 208, 210);
    lv_obj_align(list, LV_ALIGN_CENTER, 0, 8);
    lv_obj_set_style_radius(list, 22, 0);
    lv_obj_set_style_bg_color(list, lv_color_hex(0x222634), 0);
    lv_obj_set_style_border_color(list, lv_color_hex(0x4CCAE4), 0);
    lv_obj_set_style_border_width(list, 2, 0);

    lv_obj_t * button = NULL;

    button = lv_list_add_button(list, NULL, "Spotify");
    if(g_group != NULL) lv_group_add_obj(g_group, button);

    button = lv_list_add_button(list, NULL, "Amazon");
    if(g_group != NULL) lv_group_add_obj(g_group, button);

    button = lv_list_add_button(list, NULL, "YouTube");
    if(g_group != NULL) lv_group_add_obj(g_group, button);

    button = lv_list_add_button(list, NULL, "Local");
    if(g_group != NULL) lv_group_add_obj(g_group, button);
}

static void yoyopy_build_footer_scene(void) {
    lv_obj_t * screen = lv_screen_active();
    lv_obj_clean(screen);
    yoyopy_clear_group();

    lv_obj_t * label = lv_label_create(screen);
    lv_label_set_text(label, "Tap next / Double open / Hold back");
    lv_obj_align(label, LV_ALIGN_BOTTOM_MID, 0, -10);
    lv_obj_set_style_text_font(label, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(label, lv_color_hex(0xE8E8EF), 0);
}

static void yoyopy_build_carousel_scene(void) {
    lv_obj_t * screen = lv_screen_active();
    lv_obj_clean(screen);
    yoyopy_clear_group();
    yoyopy_create_card(screen, "Talk", "Carousel proof", lv_color_hex(0x4CCAE4));

    lv_obj_t * footer = lv_label_create(screen);
    lv_label_set_text(footer, "Tap next / Open");
    lv_obj_align(footer, LV_ALIGN_BOTTOM_MID, 0, -10);
    lv_obj_set_style_text_font(footer, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(footer, lv_color_hex(0xF6F6F8), 0);
}

int yoyopy_lvgl_init(void) {
    if(g_initialized) {
        return 0;
    }

    yoyopy_set_error(NULL);
    lv_init();
    g_initialized = 1;
    return 0;
}

void yoyopy_lvgl_shutdown(void) {
    if(g_draw_buf != NULL) {
        lv_free(g_draw_buf);
        g_draw_buf = NULL;
    }

    if(g_group != NULL) {
        lv_group_delete(g_group);
        g_group = NULL;
    }

    g_display = NULL;
    g_indev = NULL;
    g_flush_cb = NULL;
    g_flush_user_data = NULL;
    g_draw_buf_bytes = 0;
    g_key_head = 0;
    g_key_tail = 0;
    g_key_count = 0;
    g_initialized = 0;
    yoyopy_set_error(NULL);
}

int yoyopy_lvgl_register_display(
    int32_t width,
    int32_t height,
    uint32_t buffer_pixel_count,
    yoyopy_lvgl_flush_cb_t flush_cb,
    void * user_data
) {
    if(!g_initialized) {
        yoyopy_set_error("LVGL must be initialized before registering a display");
        return -1;
    }

    if(g_display != NULL) {
        yoyopy_set_error("display already registered");
        return -1;
    }

    if(flush_cb == NULL) {
        yoyopy_set_error("flush callback is required");
        return -1;
    }

    g_display = lv_display_create(width, height);
    if(g_display == NULL) {
        yoyopy_set_error("lv_display_create failed");
        return -1;
    }

    g_draw_buf_bytes = buffer_pixel_count * sizeof(lv_color_t);
    g_draw_buf = lv_malloc(g_draw_buf_bytes);
    if(g_draw_buf == NULL) {
        yoyopy_set_error("draw buffer allocation failed");
        return -1;
    }

    g_flush_cb = flush_cb;
    g_flush_user_data = user_data;

    lv_display_set_flush_cb(g_display, yoyopy_flush_cb);
    lv_display_set_buffers(
        g_display,
        g_draw_buf,
        NULL,
        g_draw_buf_bytes,
        LV_DISPLAY_RENDER_MODE_PARTIAL
    );

    return 0;
}

int yoyopy_lvgl_register_input(void) {
    if(!g_initialized || g_display == NULL) {
        yoyopy_set_error("display must be registered before input");
        return -1;
    }

    if(g_group == NULL) {
        g_group = lv_group_create();
        lv_group_set_default(g_group);
    }

    if(g_indev == NULL) {
        g_indev = lv_indev_create();
        if(g_indev == NULL) {
            yoyopy_set_error("lv_indev_create failed");
            return -1;
        }
        lv_indev_set_type(g_indev, LV_INDEV_TYPE_KEYPAD);
        lv_indev_set_read_cb(g_indev, yoyopy_indev_read_cb);
        lv_indev_set_group(g_indev, g_group);
    }

    return 0;
}

void yoyopy_lvgl_tick_inc(uint32_t ms) {
    if(g_initialized) {
        lv_tick_inc(ms);
    }
}

uint32_t yoyopy_lvgl_timer_handler(void) {
    if(!g_initialized) {
        return 0U;
    }

    return lv_timer_handler();
}

int yoyopy_lvgl_queue_key_event(int32_t key, int32_t pressed) {
    if(g_key_count >= KEY_QUEUE_CAPACITY) {
        yoyopy_set_error("input queue full");
        return -1;
    }

    g_key_queue[g_key_tail].key = key;
    g_key_queue[g_key_tail].pressed = pressed;
    g_key_tail = (g_key_tail + 1) % KEY_QUEUE_CAPACITY;
    g_key_count++;
    return 0;
}

int yoyopy_lvgl_show_probe_scene(int32_t scene_id) {
    if(!g_initialized || g_display == NULL) {
        yoyopy_set_error("display must be registered before showing a scene");
        return -1;
    }

    switch(scene_id) {
        case YOYOPY_LVGL_SCENE_CARD:
            yoyopy_build_card_scene();
            break;
        case YOYOPY_LVGL_SCENE_LIST:
            yoyopy_build_list_scene();
            break;
        case YOYOPY_LVGL_SCENE_FOOTER:
            yoyopy_build_footer_scene();
            break;
        case YOYOPY_LVGL_SCENE_CAROUSEL:
            yoyopy_build_carousel_scene();
            break;
        default:
            yoyopy_set_error("unknown probe scene");
            return -1;
    }

    return 0;
}

void yoyopy_lvgl_clear_screen(void) {
    if(!g_initialized || g_display == NULL) {
        return;
    }

    lv_obj_t * screen = lv_screen_active();
    lv_obj_clean(screen);
    yoyopy_clear_group();
}

const char * yoyopy_lvgl_last_error(void) {
    return g_last_error;
}

const char * yoyopy_lvgl_version(void) {
    static char version[32];
    snprintf(
        version,
        sizeof(version),
        "%d.%d.%d",
        LVGL_VERSION_MAJOR,
        LVGL_VERSION_MINOR,
        LVGL_VERSION_PATCH
    );
    return version;
}
