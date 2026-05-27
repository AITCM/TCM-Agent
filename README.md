# TCM-Agent 网络药理学智能体

TCM-Agent 是一个面向中医药系统药理学研究的多智能体分析系统，围绕中药成分解析、靶点发现、网络药理学推断与富集分析等场景，集成大语言模型、知识图谱与常用生物信息学工具，帮助研究人员更高效地完成机制探索与候选发现。

## 项目特点

- 支持中药/化合物信息查询与靶点关联分析
- 支持蛋白互作网络、分子相似度与药物-靶点活性分析
- 支持富集分析结果生成、展示与文件下载
- 支持中药-靶点知识图谱可视化
- 采用前后端分离架构，便于扩展与部署

## 技术栈

- 后端：Python Flask + Socket.IO
- 前端：React + TypeScript + Material UI
- 通信：WebSocket
- 模型：支持多种大语言模型接入

## 快速启动

### 后端

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=3000
```

### 前端

```bash
cd client
npm install
npm start
```

## 仓库状态说明（闭源）

本项目当前已设置为闭源，公开仓库中仅保留说明文档。

如有技术合作或合作开发意向，请联系：北京中医药大学 DeepTCM 中医智慧深度探索实验室，wangxt@bucm.edu.cn。