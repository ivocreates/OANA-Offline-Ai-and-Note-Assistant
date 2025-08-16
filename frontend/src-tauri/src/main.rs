#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::process::Command;
use tauri::Manager;

// Start the Python backend server
fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // Start the backend server when the app starts
            #[cfg(not(debug_assertions))]
            {
                // For production build, use bundled Python backend
                let app_handle = app.handle();
                std::thread::spawn(move || {
                    let resource_path = app_handle
                        .path_resolver()
                        .resolve_resource("backend/app.py")
                        .expect("Failed to resolve resource");
                    
                    // Start Python backend server
                    Command::new("python")
                        .arg(resource_path)
                        .spawn()
                        .expect("Failed to start backend server");
                });
            }
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
