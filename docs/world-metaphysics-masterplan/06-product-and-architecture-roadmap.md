# 06 产品与工程架构路线图

## 总体产品结构

建议星阙未来采用五个顶层工作区：

1. 排盘工作台：所有命盘、卦盘、课盘、牌阵、风水盘。
2. 知识研究院：术法百科、典籍、流派、规则库、术语库。
3. 教学训练营：课程、练习、案例拆解、考试认证。
4. 案例与验证中心：命例、事件、预测登记、统计报告。
5. AI 玄学助理：RAG、解释、合参、教学、研究、报告生成。

当前 APP 已有排盘工作台和 AI 分析雏形，下一步应补知识研究院和验证中心。

## 统一模块接口

每个术法模块都实现以下接口：

```ts
type MetaphysicsModule = {
  id: string;
  name: string;
  tradition: string;
  category: 'astrology' | 'calendar' | 'divination' | 'fengshui' | 'cards' | 'numerology' | 'physiognomy';
  inputSchema: JSONSchema;
  compute(input: unknown, config: RuleConfig): Promise<ComputedChart>;
  explain(chart: ComputedChart, context: ExplainContext): Promise<Interpretation>;
  teachingUnits: TeachingUnit[];
  evidenceProtocols: EvidenceProtocol[];
};
```

输出统一：

```ts
type ComputedChart = {
  chartId: string;
  moduleId: string;
  input: unknown;
  normalizedInput: unknown;
  config: RuleConfig;
  result: unknown;
  calculationTrace: TraceStep[];
  warnings: Warning[];
  createdAt: string;
};
```

## 规则引擎

### 规则条目

```json
{
  "id": "bazi.geju.zhengguan.success.v1",
  "name": "正官格成格条件",
  "tradition": "bazi",
  "school": "ziping",
  "source": {
    "type": "book",
    "title": "子平真诠",
    "locator": "正官格"
  },
  "conditions": [
    "月令透正官",
    "官星清纯",
    "有财印相辅",
    "无伤官重破"
  ],
  "counterConditions": [
    "伤官见官无制",
    "官杀混杂严重"
  ],
  "output": {
    "tags": ["格局", "正官"],
    "strength": "scored",
    "interpretationTemplate": "此盘具备正官格条件..."
  }
}
```

### 规则类型

- 计算规则：如何排盘。
- 判定规则：是否命中某格局/组合。
- 解释规则：命中后如何解释。
- 禁忌规则：何时不应解释。
- 冲突规则：两个流派或规则互相矛盾时如何展示。
- 研究规则：如何把规则变成可验证假设。

## 知识图谱

### 节点类型

- Tradition：传统，如 Chinese Metaphysics、Jyotish。
- System：系统，如 BaZi、Zi Wei、Tarot。
- School：流派，如 盲派、Jaimini。
- Concept：概念，如 十神、Nakshatra。
- Rule：规则。
- Source：典籍、论文、网站、教材。
- Case：案例。
- Event：事件。
- Person：人物/作者。
- Symbol：星曜、牌、卦、符文。

### 关系类型

- `belongs_to`
- `derived_from`
- `conflicts_with`
- `supports`
- `uses_input`
- `produces_output`
- `interprets`
- `verified_by`
- `disputed_by`

## AI/RAG 架构

### 资料层

- 古籍原文。
- 现代教材。
- 用户笔记。
- 案例库。
- 规则库。
- 计算结果。
- 外部开放资料。

### 检索层

- 术语标准化：同义词、繁简、拼音、梵文/英文。
- 分块策略：典籍按章/条，规则按单条，案例按事件。
- 引用强制：AI 输出必须附来源 ID。
- 可信度分层：官方文档、典籍、教材、论坛、用户笔记分权重。

### Agent 角色

- 占星研究员：负责天文、宫位、推运。
- 八字老师：负责格局、旺衰、调候。
- 三式断课师：负责奇门/六壬/太乙。
- 塔罗读牌师：负责牌阵和象征。
- 研究方法顾问：负责把断语转成可验证协议。
- 伦理守门员：拦截医疗、法律、金融、恐吓式建议。

## 数据库设计

### 核心表

- `charts`：所有盘。
- `chart_inputs`：原始输入。
- `chart_results`：计算结果 JSON。
- `rule_configs`：流派配置。
- `interpretations`：断语与解释。
- `sources`：资料来源。
- `rules`：规则库。
- `cases`：案例。
- `events`：人生/世界事件。
- `predictions`：预测登记。
- `prediction_outcomes`：结果回填。
- `research_datasets`：研究数据集。

### 事件本体

事件必须结构化，否则无法验证：

- category：职业、关系、健康、迁移、财务、事故、教育、家庭、法律。
- start_date/end_date。
- certainty：日期精度。
- severity。
- user_reported / verified_source。
- privacy_level。
- linked_chart_ids。

## 插件化

未来“世界所有玄学”不应全部塞进核心仓库。建议做插件协议：

- `module.json`：模块元数据。
- `input.schema.json`。
- `config.schema.json`。
- `compute` 服务或 WASM/JS/Python worker。
- `rules/`。
- `sources/`。
- `ui/` 可选。
- `tests/`。

这样可让新术法独立迭代，也方便商业授权牌库/专业流派插件。

## 路线图

### 0-3 个月

- 完成规则元数据系统。
- 整理现有 20 模块的输入/输出/配置。
- AI 分析增加引用和结构化断语。
- 八字、印占、星运、三式优先补 P0 规则解释。
- 建立案例/事件/预测数据表。

### 3-6 个月

- 知识研究院上线。
- 印占 Dasha/Jaimini/Ashtakavarga。
- 西占推运搜索器。
- 八字多流派对照。
- 六爻/奇门/六壬断事模板。
- 塔罗与 Geomancy 快速模块。

### 6-12 个月

- 风水户型/罗盘/飞星工作台。
- 研究验证中心。
- 教学训练营。
- 世界历法：Panchanga、Mayan、Hebrew、Islamic 基础。
- 插件市场/模块包。

### 12 个月以上

- 大规模匿名命例研究。
- 公开规则评测榜。
- 专家协作平台。
- 多语言国际化。
- 3D 天球与世界玄学知识图谱。

