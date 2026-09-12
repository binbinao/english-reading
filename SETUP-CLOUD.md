# 迁移到「云端工作」模式 —— 不再依赖本地电脑开机

## 为什么要迁移

WorkBuddy 桌面客户端的自动化任务是**本地执行**的：电脑关机 / 休眠 / 客户端未运行，任务都不会触发，而且**跳过不补发**。每天 07:30 那一期，只要早上电脑没开就没了。

WorkBuddy 微信小程序的**「云端工作」模式**把任务跑在腾讯云沙箱里，与本地开机状态完全无关，跑完还能直接推到微信小程序。这才是"每天一定有"的正确形态。

| | 本地模式（当前） | 云端工作模式（目标） |
|---|---|---|
| 执行位置 | 你的 Mac | 腾讯云沙箱 |
| 电脑关机 | ❌ 不执行、不补发 | ✅ 照常执行 |
| 结果推送 | 本地文件 + 微信小程序 | 微信小程序 / 企微 bot / 邮箱 |
| 访问本地文件 | ✅ | ❌ 沙箱隔离 |
| 访问 GitHub | ✅ SSH | ✅ HTTPS + PAT |
| 需要本地环境 | Python / git / 仓库 | 无 —— 每次都从 GitHub 克隆 |

关键差异：**云沙箱是干净的一次性环境**，看不到 `~/Documents/Github/english-reading`。所以云端任务的第一步永远是 `git clone`，最后一步是 `git push`，中间全靠仓库里已有的模板和脚本。

---

## 一次性准备：创建一个细粒度 PAT

云端沙箱推代码需要凭据。**不要**用账号级 token，用 fine-grained PAT：

1. 打开 https://github.com/settings/personal-access-tokens/new
2. **Token name**：`workbuddy-cloud-reading`
3. **Expiration**：90 天（到期重建，别选 No expiration）
4. **Repository access** → Only select repositories → 只勾 `binbinao/english-reading`
5. **Permissions** → Repository permissions → **Contents: Read and write**（其余全部留 No access）
6. 生成，复制出来的是一串以 `github_pat_` 开头的长字符串

### ⚠️ 必须选「Read and write」，选成「Read」会静默失败

实测踩过的坑：权限选成 **Read** 时，`git clone` 会**成功**（读没问题），但 `git push` 会报 403：

```
remote: Permission to binbinao/english-reading.git denied to binbinao.
fatal: unable to access 'https://github.com/binbinao/english-reading.git/': The requested URL returned error: 403
```

这个失败**只在跑的最后一刻才出现**，前面选文、排版、校验全部正常，很容易误以为配置没问题。

另外注意：`GET /repos/{owner}/{repo}` 返回的 `permissions` 字段显示的是**你账号的仓库角色**（会是 `admin: true`），**不代表 token 的实际权限**。用这个字段判断 token 能不能写是错的。

### 验证 PAT 真的能写（30 秒，建议一次性做掉）

```bash
PAT=<你的 token>
rm -rf /tmp/patcheck && git clone -q "https://$PAT@github.com/binbinao/english-reading.git" /tmp/patcheck
cd /tmp/patcheck && git config user.email "binbinao@users.noreply.github.com" && git config user.name "jiduobin"
git commit -q --allow-empty -m probe && git push -q origin HEAD:pat-check && echo "✅ 可写"
git push -q origin --delete pat-check; cd /tmp && rm -rf /tmp/patcheck
```

输出 `✅ 可写` 才说明配置正确；报 403 就回第 5 步把 Contents 改成 **Read and write**。

### 关于 Pages 权限（与云端任务无关）

启用 GitHub Pages 站点需要单独的 **Pages: Read and write** 权限，**云端任务并不需要它**
（Pages 是"从分支部署"，每次 push 后自动重建）。所以日常任务的 token 保持 Contents 读写即可，
不要为了开 Pages 而额外放宽权限。详见下面「启用 Pages」一节。

⚠️ 安全约束（务必遵守）：
- 这个 token 只对**这一个仓库**有读写权，泄了也伤不到别的项目
- 它会以明文出现在自动化任务的提示词里 —— 属于可接受范围，但**不要**把它写进仓库任何文件，也不要贴到聊天/文档里
- 一旦怀疑泄露，回上面那个页面 Revoke，重建一个即可（重建后记得改自动化提示词）

---

## 迁移步骤（手机上 5 分钟）

1. 微信搜索并打开 **WorkBuddy 小程序**，授权登录（用与桌面端同一个账号）
2. 界面上方切换到 **「云端工作」** 模式
3. 进入 **自动化** 页面 → 点 **「+」新建任务**
4. **执行频率**：周期 = 每天，时间 = **07:30**
5. 打开 **「推送到 WorkBuddy 微信小程序」**（这样结果直接在手机上能读）
6. **提示词**：把下面整段复制进去（记得把 `<PAT>` 换成你刚生成的 token）
7. 先点 **「测试运行」** 验证一次 —— 确认 GitHub 上真的多了一期、小程序里也收到了，再放手

---

## 云端任务提示词（整段复制，替换 `<PAT>`）

```
【任务】「每日英文精读」产出今天这一期：从主流外刊选 1 篇 1000–2000 词文章，标注生词与专业术语，
生成手机端可读的单页 HTML，并归档到 GitHub 仓库 english-reading。

【环境准备】云沙箱里没有本地文件，每期都从零开始，必须先克隆仓库：
    git clone https://<PAT>@github.com/binbinao/english-reading.git repo
    cd repo
    git config user.name "jiduobin"
    git config user.email "binbinao@users.noreply.github.com"
仓库里已有 template/reading-template.html、scripts/build_index.py、scripts/validate.py、
scripts/publish.sh、data/index.json，直接用，不要重写。
若克隆失败：不要凭记忆自己造模板（版式会跑偏），直接在最终回复里报告失败原因，本轮不产出。

【第 1 步 · 选文】
用联网检索找当期最新文章。来源优先：Scientific American > Quanta Magazine > Nature News >
The Guardian > MIT Technology Review >（Economist / NYT / WaPo 有付费墙，通常取不到全文，取不到就换）。
主题优先：AI / AI Agent / 工业软件 / CAE·HPC·数值仿真 / 具身智能 / 智能制造 / 半导体 / AI4S。
硬性门槛：正文 1000–2000 英文单词，必须实测，不许估算 —— 把候选正文存成 /tmp/cand.txt 后跑：
    python3 -c "import re;print(len(re.findall(r\"[A-Za-z][A-Za-z'-]*\",open('/tmp/cand.txt').read())))"
超出区间一律弃用换下一篇。先读 data/index.json，避开已推过的 title 与 sourceUrl，不要重复选。

【第 2 步 · 套模板生成 HTML】
读 template/reading-template.html，替换全部 17 个 {{占位符}}：
EPISODE（第 NNN 期，N = data/index.json 里 articles 条数 + 1，三位补零）、DATE（今天 YYYY-MM-DD）、
WORDS（实测词数）、MINUTES（WORDS/200 四舍五入）、LEVEL（CEFR: B1 / B2 / B2–C1 / C1）、
SOURCE（来源简称）、CATEGORY（主题标签）、PAGE_TITLE、TITLE、SUBTITLE、BYLINE、
SOURCE_FULL、SOURCE_URL、SOURCE_URL_TEXT、NEXT_HINT（下期候选 2–3 篇）、BODY_HTML、VOCAB_JSON。

BODY_HTML：每段一个 <p>。通用生词写成 <span class="m v" data-w="键名">原词</span>；
专业术语 / 专有名词写成 <span class="m t" data-w="键名">原词</span>。
VOCAB_JSON：JS 对象字面量（key 可不加引号），每键一条：
  key:{t:"v",w:"显示词",ipa:"/音标/",pos:"v. 动词",cn:"中文释义",ex:"改写英文例句"}
t 取 "v"（生词）或 "t"（术语），与 data-w 的键名一一对应。
标注量 25–37 条（生词 20–30 + 术语 5–10）。释义讲清用法与语境，不要只给词典直译；
例句必须是改写的新句子，不得照抄原文；禁止整句整句高亮。

【第 3 步 · 校验（不通过不许发布）】
成品写到 articles/YYYY-MM-DD.html；纯英文原文（无标注无中文）写到 articles/YYYY-MM-DD.txt。然后：
    python3 scripts/validate.py articles/YYYY-MM-DD.html
必须看到「全部校验通过」。若报「缺定义 / 未使用 / 占位符未替换 / 词数超区间」，修好再跑，直到通过。

【第 4 步 · 登记索引】
在 data/index.json 的 articles 数组最前面插入一条，字段齐全：
date / episode / source / category / title / subtitle / sourceFull / sourceUrl / pubDate /
words / level / vocabCount / termCount / url / txt
vocabCount 与 termCount 必须与 HTML 中实际条数一致。
date = 推送日；pubDate = 原文发表日期。
若当天该文件名已存在（一天内被触发多次），不要覆盖，改用 articles/YYYY-MM-DD-002.html 并相应更新 url 与 txt。

【第 5 步 · 发布】
    bash scripts/publish.sh YYYY-MM-DD
成功标志是输出「[ok] 已推送到 origin/main」。
若输出「[error] 推送失败」——这是硬失败，不可忽略：必须在最终回复里明确写出「今日已生成但未推送成功」，
并提示用户检查 PAT 是否过期或权限不足。
重跑前先 git pull --rebase，避免非快进冲突。

【第 6 步 · 交付】
用成果展示（present_files）把 articles/YYYY-MM-DD.html 交给用户 —— 这是他真正要读的成品。

【最终回复】
用中文、简洁，包含：期号 / 来源 / 标题 / 日期；词数、生词数、术语数；
2–3 句中文导览（讲了什么、为什么值得读）；推送状态。不要贴全文。

【硬性约束】
- 必须使用真实抓取到的原文，严禁编造文章内容、作者或数据。
- 若所有来源都找不到 1000–2000 词的合适文章，退而选最接近的一篇（800–2200 词），
  并在最终回复里说明偏离原因。绝不编造。
- 不要改动 template/ 与 scripts/ 下的既有文件，除非发现真实 bug（发现则修好并说明）。
```

---

## 启用 Pages（让手机上能直接打开归档首页）

Pages 站点目前**尚未启用**（`GET /repos/.../pages` 返回 404，`has_pages: false`）。
启用后归档首页就是 <https://binbinao.github.io/english-reading/>，手机上点开即可阅读。

启用方式二选一：

**A. 网页点一下（推荐，不扩大 token 权限）**

<https://github.com/binbinao/english-reading/settings/pages>
→ **Source** 选 `Deploy from a branch` → **Branch** 选 `main` / `(root)` → 保存

**B. 用 API（需要 token 额外具备 Pages 权限）**

```bash
curl -X POST -H "Authorization: Bearer $PAT" -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/binbinao/english-reading/pages \
  -d '{"source":{"branch":"main","path":"/"}}'
```

实测：只给 Contents 读写的 token 调这个接口会返回
`403 Resource not accessible by personal access token`。
注意 **Pages 权限 ≠ Contents 权限**，即使仓库角色是 `admin` 也不管用 —— 细粒度 token 必须单独勾选 Pages。

### 已试过、确认不可行的做法（别重复踩）

用 GitHub Actions 自动启用 Pages（`actions/configure-pages@v5` 配 `enablement: true`）——
运行会失败：`Create Pages site failed. Error: Resource not accessible by integration`。
**`GITHUB_TOKEN` 无权创建 Pages 站点**，这条路堵死（曾加过工作流，已撤回，见 commit `0a2914d`）。

启用后每次 `git push` 都会自动重建站点，无需任何后续操作。

---

## 迁移完成后必做：删掉本地的旧任务

否则**每天早上你会收到两份**（本地一份 + 云端一份），GitHub 上也会出现重复提交与冲突。

建议顺序：
1. 先建好云端任务，点「测试运行」，确认 GitHub 上多了一期、小程序里收到
2. 确认无误后，回到**桌面端** WorkBuddy → 自动化 → 找到「每日英文精读（生成 + 推送 GitHub）」→ **删除或停用**
3. 桌面端那条规则的任务 ID 是 `40d21f41-6dcb-420f-a717-0c74ffca53e3`

在云端验证通过之前，**先别删**本地那条 —— 它是明天 07:30 的兜底。

---

## 如果云端也满足不了（备选方案）

云沙箱若无法访问 GitHub（克隆或推送失败），还有两条退路：

**A. 云端只生成、不推送** —— 把提示词的第 0 步与第 5 步删掉，改为在沙箱内直接建模板与脚本（或把提示词里内联一份精简模板），产物通过微信小程序交付，GitHub 归档改为每周在本地补一次。

**B. GitHub Actions 定时任务** —— 完全脱离 WorkBuddy：在仓库里加一个 cron 工作流，用外部大模型 API（如腾讯 lkeap 的 OpenAI 兼容端点，密钥存 GitHub Secrets）跑生成脚本。优点是 100% 自主可控；缺点是需要你自己维护脚本、需要单独的 API key、且无法把结果推到微信小程序。

需要哪条，说一声即可。
