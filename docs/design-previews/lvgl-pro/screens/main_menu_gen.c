/**
 * @file main_menu_gen.c
 * @brief Template source file for LVGL objects
 */

/*********************
 *      INCLUDES
 *********************/

#include "main_menu_gen.h"
#include "../yoyopod_design_preview.h"

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/***********************
 *  STATIC VARIABLES
 **********************/

/***********************
 *  STATIC PROTOTYPES
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

lv_obj_t * main_menu_create(void)
{
    LV_TRACE_OBJ_CREATE("begin");


    static bool style_inited = false;

    if (!style_inited) {

        style_inited = true;
    }

    lv_obj_t * lv_obj_0 = lv_obj_create(NULL);
    lv_obj_set_name_static(lv_obj_0, "main_menu_#");
    lv_obj_set_flex_flow(lv_obj_0, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_bg_color(lv_obj_0, lv_color_hex(0x12151c), 0);
    lv_obj_set_style_bg_opa(lv_obj_0, (255 * 100 / 100), 0);
    lv_obj_set_style_pad_all(lv_obj_0, 16, 0);
    lv_obj_set_style_pad_row(lv_obj_0, 12, 0);

    lv_obj_t * lv_label_0 = lv_label_create(lv_obj_0);
    lv_label_set_text(lv_label_0, "Main menu smoke test");
    
    lv_obj_t * lv_button_0 = lv_button_create(lv_obj_0);
    lv_obj_t * lv_label_1 = lv_label_create(lv_button_0);
    lv_label_set_text(lv_label_1, "Listen");
    
    lv_obj_t * lv_button_1 = lv_button_create(lv_obj_0);
    lv_obj_t * lv_label_2 = lv_label_create(lv_button_1);
    lv_label_set_text(lv_label_2, "Talk");
    
    lv_obj_t * lv_button_2 = lv_button_create(lv_obj_0);
    lv_obj_t * lv_label_3 = lv_label_create(lv_button_2);
    lv_label_set_text(lv_label_3, "Ask");
    
    lv_obj_t * lv_button_3 = lv_button_create(lv_obj_0);
    lv_obj_t * lv_label_4 = lv_label_create(lv_button_3);
    lv_label_set_text(lv_label_4, "Setup");

    LV_TRACE_OBJ_CREATE("finished");

    return lv_obj_0;
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

