local status_ok, dap = pcall(require, "dap")
if not status_ok then
    print("Failed to load dap")
    return
end

dap.adapters.python = {
    type = "executable",
    command = "python",
    args = { "-m", "debugpy.adapter" },
}

dap.configurations.python = {
    {
        type = "python",
        request = "launch",
        name = "${workspaceFolderBasename}",
        program = "run.py",
        cwd = "${workspaceFolder}",
    },
}
