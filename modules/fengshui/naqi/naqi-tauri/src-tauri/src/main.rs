#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::menu::{Menu, MenuItem, PredefinedMenuItem, Submenu};
use tauri::{Emitter, Runtime};

fn build_menu<R: Runtime>(app: &tauri::AppHandle<R>) -> tauri::Result<Menu<R>> {
  let export_png = MenuItem::with_id(app, "export_png", "导出 PNG", true, Some("CmdOrCtrl+E"))?;
  let export_config = MenuItem::with_id(
    app,
    "export_config",
    "导出项目文件…",
    true,
    Some("CmdOrCtrl+Shift+S"),
  )?;
  let import_config = MenuItem::with_id(
    app,
    "import_config",
    "导入项目文件…",
    true,
    Some("CmdOrCtrl+Shift+O"),
  )?;
  let open_recent = MenuItem::with_id(
    app,
    "open_recent",
    "最近项目文件…",
    true,
    Some("CmdOrCtrl+Shift+L"),
  )?;
  let manual_rect = MenuItem::with_id(app, "manual_rect", "手动框选房屋", true, Some("CmdOrCtrl+Shift+M"))?;
  let reset_rect = MenuItem::with_id(app, "reset_rect", "重置房屋框", true, Some("CmdOrCtrl+Shift+R"))?;
  let clear_markers = MenuItem::with_id(app, "clear_markers", "清空标记", true, Some("CmdOrCtrl+Shift+X"))?;
  let preferences = MenuItem::with_id(app, "preferences", "偏好设置…", true, Some("CmdOrCtrl+,"))?;
  let show_help = MenuItem::with_id(app, "show_help", "使用说明", true, Some("CmdOrCtrl+/"))?;

  let app_menu = Submenu::with_items(
    app,
    "荀爽纳气风水",
    true,
    &[
      &PredefinedMenuItem::about(app, None, None)?,
      &PredefinedMenuItem::separator(app)?,
      &preferences,
      &PredefinedMenuItem::separator(app)?,
      &PredefinedMenuItem::services(app, None)?,
      &PredefinedMenuItem::separator(app)?,
      &PredefinedMenuItem::hide(app, None)?,
      &PredefinedMenuItem::hide_others(app, None)?,
      &PredefinedMenuItem::show_all(app, None)?,
      &PredefinedMenuItem::separator(app)?,
      &PredefinedMenuItem::quit(app, None)?,
    ],
  )?;

  let file_menu = Submenu::with_items(
    app,
    "文件",
    true,
    &[
      &import_config,
      &export_config,
      &open_recent,
      &PredefinedMenuItem::separator(app)?,
      &export_png,
      &PredefinedMenuItem::separator(app)?,
      &PredefinedMenuItem::close_window(app, None)?,
    ],
  )?;

  let edit_menu = Submenu::with_items(
    app,
    "编辑",
    true,
    &[
      &PredefinedMenuItem::undo(app, None)?,
      &PredefinedMenuItem::redo(app, None)?,
      &PredefinedMenuItem::separator(app)?,
      &PredefinedMenuItem::cut(app, None)?,
      &PredefinedMenuItem::copy(app, None)?,
      &PredefinedMenuItem::paste(app, None)?,
      &PredefinedMenuItem::select_all(app, None)?,
    ],
  )?;

  let tools_menu = Submenu::with_items(
    app,
    "工具",
    true,
    &[
      &manual_rect,
      &reset_rect,
      &PredefinedMenuItem::separator(app)?,
      &clear_markers,
    ],
  )?;

  let view_menu = Submenu::with_items(
    app,
    "视图",
    true,
    &[
      &PredefinedMenuItem::fullscreen(app, None)?,
    ],
  )?;

  let window_menu = Submenu::with_items(
    app,
    "窗口",
    true,
    &[
      &PredefinedMenuItem::minimize(app, None)?,
      &PredefinedMenuItem::maximize(app, None)?,
      &PredefinedMenuItem::separator(app)?,
      &PredefinedMenuItem::close_window(app, None)?,
    ],
  )?;

  let help_menu = Submenu::with_items(app, "帮助", true, &[&show_help])?;

  Menu::with_items(
    app,
    &[
      &app_menu,
      &file_menu,
      &edit_menu,
      &tools_menu,
      &view_menu,
      &window_menu,
      &help_menu,
    ],
  )
}

fn emit<R: Runtime>(app: &tauri::AppHandle<R>, event: &str) {
  let _ = app.emit(event, ());
}

fn main() {
  tauri::Builder::default()
    .menu(build_menu)
    .on_menu_event(|app, event| {
      let id = event.id();
      if id == "export_png" {
        emit(app, "menu-export-png");
      } else if id == "export_config" {
        emit(app, "menu-export-config");
      } else if id == "import_config" {
        emit(app, "menu-import-config");
      } else if id == "open_recent" {
        emit(app, "menu-open-recent");
      } else if id == "manual_rect" {
        emit(app, "menu-manual-rect");
      } else if id == "reset_rect" {
        emit(app, "menu-reset-rect");
      } else if id == "clear_markers" {
        emit(app, "menu-clear-markers");
      } else if id == "preferences" {
        emit(app, "menu-preferences");
      } else if id == "show_help" {
        emit(app, "menu-show-help");
      }
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
