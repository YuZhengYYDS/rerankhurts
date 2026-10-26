# 仓库元数据

- `MANIFEST.json`：当前仓库文件的大小与 SHA-256；自身不列入自身哈希。
- `release_status.json`：稿件、作者和实验完成状态。
- `data_layout.json`：根目录数据迁移记录，包含原路径、新路径和原始文件身份。

历史实验 manifest 保留运行时记录的路径和身份。维护中的校验器按 `../rerankhuts/paths.py` 的固定映射读取迁移后的文件，并比较原始哈希。

发布 ZIP 内根目录的 `MANIFEST.json` 由打包工具单独生成，用来校验该 ZIP 的实际成员。
