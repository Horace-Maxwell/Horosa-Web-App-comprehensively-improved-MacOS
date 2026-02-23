# runtime 目录说明

该目录用于存放**本机生成的运行时缓存**（例如打包的 Java/Python 运行时、离线 bundle）。

- GitHub 版本默认不提交这些大体积二进制文件。
- 在任意 Mac 上首次运行 `Horosa_OneClick_Mac.command` 时会自动准备所需环境和构建产物。
- 如果你需要制作“完全离线包”，可以本地执行 `Prepare_Runtime_Mac.command` 生成内容，再自行打包分发（不建议直接提交到 GitHub 仓库）。
