# 📖 Plot Annotation Tool

故事情节AB测试与ELO评分系统 - 用于对比和标注不同版本的故事情节。

## 🎯 功能特点

### 1. 因果图可视化 (Causal Graph)
- 使用 Pyvis 库渲染交互式因果图
- 支持节点类型区分（milestone、escalation、climax）
- 悬停显示完整事件描述
- 层级布局展示因果关系

### 2. AB测试比较
- 并排显示两个Plot进行对比
- 支持查看故事树、冲突分析、完整剧本

### 3. 多维度ELO评分
支持6个评分维度：
- **Surprise (惊喜度)**: 情节转折的意外程度
- **Valence (情感效价)**: 情感正负向（VAD模型）
- **Arousal (情感唤醒)**: 情感激烈程度（VAD模型）
- **Dominance (控制感)**: 角色掌控程度（VAD模型）
- **Conflict (冲突质量)**: 冲突深度和戏剧张力
- **Coherence (连贯性)**: 情节逻辑连贯性

### 4. 排行榜
- 各维度ELO分数排名
- 综合评分排行
- 热力图可视化

### 5. 数据管理
- 支持JSON文件上传
- 评分结果导出
- 比较历史记录

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
streamlit run app.py
```

### 使用示例数据
上传 `sample_data.json` 文件进行测试。

## 📁 JSON数据格式

```json
{
  "title": "故事标题",
  "genre": "类型",
  "status": "状态",
  "pruned_tree": "故事树结构（文本格式）",
  "causal_graph": {
    "characters": [
      {"name": "角色名", "role": "protagonist/supporting/antagonist"}
    ],
    "event_nodes": [
      {
        "id": "3.1",
        "name": "事件描述",
        "type": "milestone/escalation/climax",
        "characters_involved": ["角色1", "角色2"]
      }
    ],
    "conflicts": [
      {
        "event_id": "3.1",
        "type": "Person vs. Person",
        "character1": "角色1",
        "character2": "角色2",
        "description": "冲突描述"
      }
    ],
    "edges": [
      {
        "from": "3.1",
        "to": "3.2",
        "type": "causal",
        "description": "因果关系描述"
      }
    ]
  },
  "final_plot": "完整剧本（Markdown格式）"
}
```

## 📊 ELO评分系统

- 初始分数：1500
- K因子：32
- 支持三种结果：A胜、B胜、平局

### 计算公式
```
Expected Score: E_A = 1 / (1 + 10^((R_B - R_A) / 400))
New Rating: R'_A = R_A + K * (S_A - E_A)
```

## 🎨 界面预览

### 比较标注页
- 左右并排显示两个Plot
- 因果图交互可视化
- 多维度评分滑块

### 排行榜页
- 各维度分数排名
- 综合评分统计

### 历史记录页
- 所有比较记录
- 时间戳和备注

## 📝 标注流程

1. **上传数据**: 在侧边栏上传JSON文件
2. **选择对比**: 选择两个Plot进行比较
3. **查看详情**: 浏览因果图、故事树、冲突、剧本
4. **评分标注**: 在6个维度上选择获胜者
5. **提交结果**: 提交评分，更新ELO
6. **查看排行**: 查看排行榜了解当前排名
7. **导出数据**: 导出评分结果用于后续分析

## 🛠 技术栈

- **Streamlit**: UI框架
- **NetworkX**: 图数据结构
- **Pyvis**: 网络图可视化
- **Pandas**: 数据处理

## 📄 License

MIT License
