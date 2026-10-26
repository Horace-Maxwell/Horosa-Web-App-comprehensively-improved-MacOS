//! 应用菜单。文案经 shell_text 按界面简繁取(单源 shell_strings.json);页面切简繁时重建。

use super::*;

pub(crate) fn build_menu<R: Runtime>(app: &tauri::AppHandle<R>) -> tauri::Result<Menu<R>> {
    let preferences = MenuItem::with_id(
        app,
        MENU_OPEN_PREFERENCES,
        &shell_text("menu.preferences"),
        true,
        Some("CmdOrCtrl+,"),
    )?;
    let check_updates = MenuItem::with_id(
        app,
        MENU_CHECK_UPDATES,
        &shell_text("menu.check_updates"),
        true,
        Some("CmdOrCtrl+U"),
    )?;
    let reinstall_runtime = MenuItem::with_id(
        app,
        MENU_REINSTALL_RUNTIME,
        &shell_text("menu.reinstall_runtime"),
        true,
        None::<&str>,
    )?;
    let restart_services = MenuItem::with_id(
        app,
        MENU_RESTART_SERVICES,
        &shell_text("menu.restart_services"),
        true,
        None::<&str>,
    )?;
    // Translocation 自助搬迁:zip 通道用户从「下载」直接运行时,自更新链路
    // 找不到真实 App 路径——菜单一键拷入「应用程序」并重开(菜单事件=主线程,弹确认框安全)。
    let relocate_app = MenuItem::with_id(
        app,
        MENU_RELOCATE_APP,
        &shell_text("menu.relocate_app"),
        true,
        None::<&str>,
    )?;
    let show_main_window = MenuItem::with_id(
        app,
        MENU_SHOW_MAIN_WINDOW,
        &shell_text("menu.show_main_window"),
        true,
        Some("CmdOrCtrl+1"),
    )?;
    let show_diagnostics = MenuItem::with_id(
        app,
        MENU_SHOW_DIAGNOSTICS,
        &shell_text("menu.show_diagnostics"),
        true,
        Some("CmdOrCtrl+2"),
    )?;
    let open_logs = MenuItem::with_id(
        app,
        MENU_OPEN_LOGS,
        &shell_text("menu.open_logs"),
        true,
        None::<&str>,
    )?;
    let open_data = MenuItem::with_id(
        app,
        MENU_OPEN_DATA,
        &shell_text("menu.open_data"),
        true,
        None::<&str>,
    )?;
    let open_runtime = MenuItem::with_id(
        app,
        MENU_OPEN_RUNTIME,
        &shell_text("menu.open_runtime"),
        true,
        None::<&str>,
    )?;
    let reload_main = MenuItem::with_id(
        app,
        MENU_RELOAD_MAIN,
        &shell_text("menu.reload_main"),
        true,
        Some("CmdOrCtrl+R"),
    )?;
    let open_releases = MenuItem::with_id(
        app,
        MENU_OPEN_RELEASES,
        &shell_text("menu.open_releases"),
        true,
        None::<&str>,
    )?;
    let zoom_in = MenuItem::with_id(
        app,
        MENU_ZOOM_IN,
        &shell_text("menu.zoom_in"),
        true,
        Some("CmdOrCtrl+="),
    )?;
    let zoom_out = MenuItem::with_id(
        app,
        MENU_ZOOM_OUT,
        &shell_text("menu.zoom_out"),
        true,
        Some("CmdOrCtrl+-"),
    )?;
    let zoom_reset = MenuItem::with_id(
        app,
        MENU_ZOOM_RESET,
        &shell_text("menu.zoom_reset"),
        true,
        Some("CmdOrCtrl+0"),
    )?;

    let app_menu = Submenu::with_items(
        app,
        APP_NAME,
        true,
        &[
            &PredefinedMenuItem::about(app, None, None)?,
            &PredefinedMenuItem::separator(app)?,
            &preferences,
            &PredefinedMenuItem::separator(app)?,
            &check_updates,
            &reinstall_runtime,
            &restart_services,
            &relocate_app,
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
        &shell_text("menu.file"),
        true,
        &[
            &show_main_window,
            &show_diagnostics,
            &PredefinedMenuItem::separator(app)?,
            &open_runtime,
            &open_logs,
            &open_data,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::close_window(app, None)?,
        ],
    )?;

    let edit_menu = Submenu::with_items(
        app,
        &shell_text("menu.edit"),
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

    let view_menu = Submenu::with_items(
        app,
        &shell_text("menu.view"),
        true,
        &[
            &reload_main,
            &PredefinedMenuItem::separator(app)?,
            &zoom_in,
            &zoom_out,
            &zoom_reset,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::fullscreen(app, None)?,
            &PredefinedMenuItem::maximize(app, None)?,
        ],
    )?;

    let window_menu = Submenu::with_items(
        app,
        &shell_text("menu.window"),
        true,
        &[
            &PredefinedMenuItem::minimize(app, None)?,
            &PredefinedMenuItem::maximize(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::close_window(app, None)?,
        ],
    )?;

    let help_menu = Submenu::with_items(app, &shell_text("menu.help"), true, &[&open_releases])?;

    Menu::with_items(
        app,
        &[
            &app_menu,
            &file_menu,
            &edit_menu,
            &view_menu,
            &window_menu,
            &help_menu,
        ],
    )
}
