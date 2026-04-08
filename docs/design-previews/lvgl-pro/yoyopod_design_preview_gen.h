/**
 * @file yoyopod_design_preview_gen.h
 */

#ifndef YOYOPOD_DESIGN_PREVIEW_GEN_H
#define YOYOPOD_DESIGN_PREVIEW_GEN_H

#ifndef UI_SUBJECT_STRING_LENGTH
#define UI_SUBJECT_STRING_LENGTH 256
#endif

#ifdef __cplusplus
extern "C" {
#endif

/*********************
 *      INCLUDES
 *********************/

#ifdef LV_LVGL_H_INCLUDE_SIMPLE
    #include "lvgl.h"
    #include "src/core/lv_obj_class_private.h"
#else
    #include "lvgl/lvgl.h"
    #include "lvgl/src/core/lv_obj_class_private.h"
#endif



/*********************
 *      DEFINES
 *********************/

#define UNIT_XS 4

#define UNIT_SM 8

#define UNIT_MD 12

#define UNIT_LG 16

#define UNIT_XL 24

#define BG lv_color_hex(0x12151c)

#define SURFACE lv_color_hex(0x1c212a)

#define SURFACE_RAISED lv_color_hex(0x232834)

#define SURFACE_BORDER lv_color_hex(0x4a4f5c)

#define INK lv_color_hex(0xf3f7fa)

#define MUTED lv_color_hex(0x99a0ad)

#define MUTED_DIM lv_color_hex(0x6f7684)

#define SUCCESS lv_color_hex(0x3ddd53)

#define DANGER lv_color_hex(0xff675d)

#define LISTEN_ACCENT lv_color_hex(0x69ea79)

#define LISTEN_SOFT lv_color_hex(0x468f53)

#define LISTEN_DIM lv_color_hex(0x34593c)

#define LISTEN_CARD lv_color_hex(0x243532)

#define LISTEN_HALO lv_color_hex(0x23402e)

#define LISTEN_HALO_OUTLINE lv_color_hex(0x2c5037)

#define TALK_ACCENT lv_color_hex(0x52dcff)

#define TALK_DIM lv_color_hex(0x2e5764)

#define ASK_ACCENT lv_color_hex(0xffd549)

#define ASK_DIM lv_color_hex(0x705c21)

#define SETUP_ACCENT lv_color_hex(0xb7bec8)

#define SETUP_DIM lv_color_hex(0x4d545c)

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 * GLOBAL VARIABLES
 **********************/

/*-------------------
 * Permanent screens
 *------------------*/

/*----------------
 * Global styles
 *----------------*/

/*----------------
 * Fonts
 *----------------*/

/*----------------
 * Images
 *----------------*/

/*----------------
 * Subjects
 *----------------*/

/**********************
 * GLOBAL PROTOTYPES
 **********************/

/*----------------
 * Event Callbacks
 *----------------*/

/**
 * Initialize the component library
 */

void yoyopod_design_preview_init_gen(const char * asset_path);

/**********************
 *      MACROS
 **********************/

/**********************
 *   POST INCLUDES
 **********************/

/*Include all the widgets, components and screens of this library*/
#include "screens/hub_gen.h"
#include "screens/main_menu_gen.h"

#ifdef __cplusplus
} /*extern "C"*/
#endif

#endif /*YOYOPOD_DESIGN_PREVIEW_GEN_H*/