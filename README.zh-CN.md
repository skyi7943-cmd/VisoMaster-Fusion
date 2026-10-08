# VisoMaster Fusion 简体中文本地化版

[English](./README.md) | **简体中文**

VisoMaster Fusion 是一款桌面端 AI 人脸替换、增强与编辑软件，支持图片、视频、摄像头和虚拟摄像头工作流。项目提供多种换脸与人脸修复模型、精细的人脸检测和遮罩控制、批量任务、VR180 处理，以及基于 CUDA、TensorRT 和 ONNX Runtime 的 GPU 加速推理。

本仓库是 [VisoMasterFusion/VisoMaster-Fusion](https://github.com/VisoMasterFusion/VisoMaster-Fusion) 的简体中文本地化分支。核心视频处理、换脸推理、模型加载和 GPU 调度算法均保持原样，汉化实现集中在独立的界面国际化层和离线翻译资源中。

> [!IMPORTANT]
> 本地化分支不会提供、重新打包或重新下载 AI 模型权重。请仅从原项目仓库及其官方发布页面获取 VisoMaster Fusion 和便携启动器。

## 中文本地化内容

本次汉化覆盖主程序与便携启动器中的主要用户界面，包括：

- 主界面的菜单、按钮、标签、导航栏、标签页和状态信息；
- 视频换脸设置、模型选择、相似度、强度和关键点相关参数；
- 人脸检测、识别、追踪、对齐、解析器及遮罩设置；
- 人脸修复、帧增强、表情编辑、姿态与颜色处理选项；
- CUDA、TensorRT、ONNX Runtime、线程、显存和性能设置说明；
- 视频与图片导入、播放器、时间轴、任务管理、录制和导出流程；
- 工具提示、确认弹窗、错误提示、进度信息和便携启动器维护功能。

翻译资源位于 `app/ui/translations/zh_CN.json`，目前包含 1,171 条离线翻译。模型文件名、Python 标识符、内部配置键、命令行参数、API 名称和其他技术标识符不会被翻译。

## 国际化设计

- 默认界面语言为简体中文；
- 设置页面可在“简体中文”和“English”之间切换；
- 翻译文本与业务逻辑分离，新增界面文本可继续加入 JSON 语言资源；
- 下拉选项显示翻译文本，但保存和传递的仍是原始规范值，避免影响模型及处理逻辑；
- 工作区文件不保存界面语言，减少语言切换对现有工作区和用户配置的影响；
- 中文文本使用原有 Qt 布局自动调整，不改变主题、图标和快捷键体系。

## 主要功能

### 人脸替换与编辑

- 支持 Inswapper128、InStyleSwapper、SimSwap、GhostFace、CSCS 和 DeepFaceLive DFM 等模型；
- 支持多张源人脸、人脸嵌入、相似度阈值和可选 ByteTrack 追踪；
- 提供人脸相似度、关键点替换、人脸调整、表情编辑和姿态控制；
- 可处理图片、视频、摄像头以及虚拟摄像头画面。

### 遮罩、修复与增强

- 提供遮挡、XSeg、文本提示、人脸解析、边缘、侧脸角度及嘴部遮罩；
- 支持多种人脸修复器、二次修复、自动混合、GFPGAN-1024 和帧增强器；
- 支持 ReF-LDM 单步与 DDIM 降噪模式；
- 包括自动着色、颜色迁移、纹理迁移、差分、MPEG 伪影、眼睛和嘴部修复等工具。

### 视频、任务与输出

- 时间轴标记和逐帧参数保存；
- 输出区间、分段渲染和问题帧扫描；
- 工作区、任务队列及无人值守批处理；
- 图片和视频输出、音频处理、质量控制及 FFmpeg 参数。

## 使用方法

### 便携版

如果已经安装原项目的便携版，可将本分支代码应用到同一项目目录，并继续使用原来的 `Start.bat` 或便携启动方式。不要删除或移动现有的 `models`、依赖环境及用户工作区文件。

### 开发环境

```powershell
git clone https://github.com/skyi7943-cmd/VisoMaster-Fusion.git
cd VisoMaster-Fusion
git switch feature/zh-cn-localization
```

依赖安装和模型准备方式与原项目一致。已经配置好的便携环境无需重复下载模型或重新安装 CUDA、TensorRT、PyTorch 和 ONNX Runtime。

启动主程序：

```powershell
python main.py
```

## 语言切换

启动程序后，在设置页面找到“语言”选项：

- 选择“简体中文”显示中文界面；
- 选择“English”恢复英文界面。

语言切换不会改写模型名称、输出路径、处理参数键或已有项目数据。

## 验证情况

当前本地化实现已进行以下静态与界面级检查：

- Python 语法编译检查；
- JSON 翻译资源加载和键值检查；
- 主窗口与启动器的离屏启动检查；
- 简体中文和英文界面切换检查；
- 下拉选项显示值与内部规范值分离检查；
- 确认未修改 `app/processors`、模型文件、AI 权重及 GPU 推理算法。

尚未在所有显卡、模型和视频格式组合上完成实际 GPU 长时间处理测试。完整推理性能与输出质量仍应在目标设备上验证。

## 与上游同步

本仓库保留原作者仓库作为上游来源。同步上游更新时，可使用：

```powershell
git fetch upstream
git switch main
git merge upstream/main
```

如果上游界面新增或修改了文本，需要相应更新 `app/ui/translations/zh_CN.json`，并重新检查中文布局。

## 原项目与致谢

- 原项目：[VisoMasterFusion/VisoMaster-Fusion](https://github.com/VisoMasterFusion/VisoMaster-Fusion)
- 原始 VisoMaster 作者：[@argenspin](https://github.com/argenspin)、[@Alucard24](https://github.com/Alucard24)
- 本地化分支维护者：[@skyi7943-cmd](https://github.com/skyi7943-cmd)

感谢 VisoMaster Fusion 的原作者、维护者及社区贡献者。本地化工作的目的，是让简体中文用户更容易理解和使用原项目，不改变原项目的版权归属。

## 许可证与使用责任

本项目继续遵循原仓库的 [GNU General Public License v3.0](./LICENSE)。发布修改版本时，应保留许可证和版权信息，并按照 GPLv3 提供相应源代码。

人脸替换技术仅应在合法、合规、获得必要授权且尊重他人隐私的情况下使用。用户需自行承担内容制作和传播所产生的责任，不得将本软件用于欺骗、骚扰、诽谤、侵犯隐私或其他违法用途。
