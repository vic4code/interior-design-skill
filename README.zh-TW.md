# Interior Design Skill

**講出你想住的樣子，探索設計，讓完整交付直接在瀏覽器打開。**

[English](README.md) · 繁體中文

支援 **Codex、Claude Code、Cursor、GitHub Copilot**。告訴 agent 生活需求、喜歡的風格與要放的東西，它會整理空間提案、製作 image gen 效果圖、準備尺寸圖冊，最後自動開啟同一個本機檢視頁。提供平面圖與量測會更精準；沒有也能先用清楚標示的假設開始。

## 你會得到什麼

**一個瀏覽器頁面，就能看懂空間、比較設計，並和設計師或施工團隊討論如何落實。**

| 檢視模式 | 交付內容 |
| --- | --- |
| **平面配置** | 保留實際房型的乾淨配置圖，清楚呈現家具位置與動線。 |
| **3D 擺設** | 一開始就能看見室內的互動模型，可旋轉、縮放，也能恢復完整外牆。 |
| **設計效果** | 真正用 image gen 製作的風格方案，依空間與視角選圖，並與各自底圖對照。 |
| **機電配置** | 照明插座提案，以及已提供的空調或給排水參考圖，保留來源與覆核狀態。 |
| **工程圖面** | 尺寸平面、立面、剖面、櫃體詳圖與表單；下載 PDF／SVG，並提供已產出的 DXF／CSV。 |

Agent 會依各房間的**實際多邊形面積或提供面積、用途與設計重點**，在約定的圖片數量內安排視角。大空間、多用途空間會有更完整的涵蓋；實際生成完成的圖片才會進入同一個圖庫，視角清單本身不算效果圖。

平面配置回答「**東西放哪裡**」，工程圖面回答「**尺寸、高度、材料與接合怎麼做**」。機電依專案資料呈現：公開範例包含照明／插座意向，完整迴路、空調與給排水設計需要對應資料和專業工種覆核。

公開範例與既有專案使用同一套前端及交付格式。多房、不規則的原生專案保留自己的幾何、圖號與已知量測；矩形入門生成器是選用工具，未知尺寸不會被補成假資料。

## 同一個空間，四種風格

保留同一個合成空間、門窗、家具配置與基底視角，透過 image gen 比較四種方案。預覽圖統一為 **900 × 675**，尺寸與比例一致。

| Mid-century Modern／MCM | Japandi／日系北歐 |
| --- | --- |
| [![MCM：胡桃木、橄欖綠布面與暖光](docs/showcase/same-space/mcm/preview.jpg)](docs/showcase/same-space/mcm/presentation.jpg) | [![Japandi：淺橡木、亞麻與自然石材](docs/showcase/same-space/japandi/preview.jpg)](docs/showcase/same-space/japandi/presentation.jpg) |
| 胡桃木、橄欖綠與溫潤復古比例。 | 淺木、織物與安靜的自然色調。 |
| **Contemporary／當代現代** | **Bauhaus／包浩斯** |
| [![當代現代：柔軟布面、石材與節制對比](docs/showcase/same-space/contemporary/preview.jpg)](docs/showcase/same-space/contemporary/presentation.jpg) | [![Bauhaus：鍍鉻、皮革與節制原色](docs/showcase/same-space/bauhaus/preview.jpg)](docs/showcase/same-space/bauhaus/presentation.jpg) |
| 圓潤量體、觸感布料與石材。 | 金屬管架、黑皮革與幾何色彩。 |

這四張**確實以同一張底圖作為 image gen 輸入**，不是四個無關的房子。可比較[模型底圖](docs/showcase/same-space/base.jpg)與[生成紀錄](docs/showcase/same-space/README.md)。生成圖用來發展外觀，家具與表面細節可能偏移；尺寸與技術細節仍以來源模型為準，採用變更後須回寫模型才能發行製作。

## 從需求開始使用

```bash
npx skills add vic4code/interior-design-skill --skill interior-design
```

> 使用 interior-design。我想要溫暖客廳，有閱讀區、收納和工作角落。用同一個格局比較 MCM、Japandi 和 Bauhaus，安排足夠的 image gen 視角呈現各區。給我平面配置、互動 3D、可用的機電協調與尺寸圖冊，完成後全部在瀏覽器打開。平面圖與量測之後可以補。

Agent 負責整理資料與執行工具；有舊專案就使用舊專案。尺寸不足時會列明假設與下一步量測。可交付項目取決於平台的圖片／模型工具與專案資料；[Host 相容性](docs/agent-compatibility.md)分開記錄安裝檢查與實際流程測試。

## 實際可下載的圖面

可重現的合成 **8 張 A3 範例**，共用空間尺寸並提供各風格的材料色調：

| 尺寸配置平面 · A101 | 櫃體三視圖 · J301 |
| --- | --- |
| [![標示家具、門窗及尺寸鏈的配置平面](docs/showcase/drawings/A101.svg)](docs/showcase/drawings/A101.svg) | [![標示板厚與內淨尺寸的櫃體三視圖](docs/showcase/drawings/J301.svg)](docs/showcase/drawings/J301.svg) |
| **櫃體剖面 · J401** | **照明插座提案 · A102** |
| [![標示層板高度、板厚及介面問題的剖面圖](docs/showcase/drawings/J401.svg)](docs/showcase/drawings/J401.svg) | [![含燈具編號與高度的照明插座協調圖](docs/showcase/drawings/A102.svg)](docs/showcase/drawings/A102.svg) |

[完整 PDF](docs/showcase/drawings/design-coordination.pdf) · [交付 ZIP](docs/showcase/design-development-S01.zip) · [平面 DXF](docs/showcase/drawings/plan.dxf) · [櫃體尺寸表](docs/showcase/drawings/joinery.csv) · [施工前確認事項](docs/showcase/drawings/issues.csv)。

實際專案圖冊應有用途標籤、室內尺寸鏈、門窗、剖面詳圖索引、構件資訊及材料五金決策，不能只有模型輪廓與外框尺寸。模型衍生的協調圖，仍需完成現場、產品、固定方式與工種覆核，才能發行施工／製作版本。

## 直接試用完整範例

在 checkout 中使用單一入口，產出四種風格並**自動開啟瀏覽器**：

```bash
cd skills/interior-design
bash scripts/setup.sh
.venv/bin/python scripts/interior_design.py demo --out /path/to/my-design
```

輸出整理在 `drawings/` 與 `review/`。範例內附以基底圖生成的效果圖與對應範例幾何，不呼叫付費圖片 API，也不需跑 Blender 渲染。真正的新方案由 agent 使用平台的 image gen 工具製作；平常由 agent 替你執行流程，這些指令也可直接本機試用。

Python 3.11+ 執行出圖工具，Node.js 建置前端；Blender 4.3+ 僅用於原生模型擷取／建模與選用的模型渲染。Image gen 需要平台工具或已設定的服務，權限、額度與可能費用依服務而定。簡化幾何與基底視角可減少精細材質與本機渲染工作，但不保證生成圖與 Blender 幾何完全一致。

Windows：用 `py -m venv .venv` 建立環境，以 `.venv\Scripts\python -m pip install -r scripts/requirements.lock.txt` 安裝依賴，再使用該 Python 執行單一入口。

## 可攜、清楚的 skill 結構

`SKILL.md` 負責主流程，`references/` 依需要載入細節，`assets/` 放範例資料、前端，以及內附的 **Taste + UI UX Pro Max** 指引與搜尋依賴。`scripts/interior_design.py` 是唯一入口，內部實作集中在 `scripts/_internal/`。

[整合檢視流程](skills/interior-design/references/browser-review.md) · [既有原生專案](skills/interior-design/references/native-handoff.md) · [設計依賴](skills/interior-design/references/design-dependencies.md) · [Host 相容性](docs/agent-compatibility.md) · [驗證紀錄](docs/verification.md) · [貢獻方式](CONTRIBUTING.md)。

原創程式與合成資產採 [MIT](LICENSE)。內附依賴保留其授權，詳見[第三方聲明](skills/interior-design/THIRD_PARTY_NOTICES.md)。不包含私人專案內容。
