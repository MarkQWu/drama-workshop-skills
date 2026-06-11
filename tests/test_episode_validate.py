"""episode_validate.py 测试。

fixtures 复刻 2026-05-20 compaction 故障的缺陷类型（场景头错格式、
缺边界标记、缺 CONTINUITY、缺元数据、缺钩子/预告标签等），
确保 validator 能机械捕获当时全部 14 项格式类缺陷。
"""
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "short-drama" / "scripts" / "episode_validate.py"

GOOD_AI_LIVE = """# 第1集：废物女婿

> 本集关键词：入赘受辱、隐藏战神、旧疤疑云
> 本集爽点：身份反差、直接打脸、危机钩
> 前情提要：无（本剧第一集）

---

## 1-1 · 内 · 苏家餐厅 · 日

**出场人物：** 陈九州、王秀芳
**出场道具：** 缺口瓷碗

△ 一只缺口瓷碗被推到餐桌最边上。

**王秀芳**（冷笑）：吃白饭的也配上桌？

**陈九州**：妈，我来收拾。

（BGM：低音厚重，每击留三秒静默）

---

## 1-2 · 外 · 小区门口 · 夜

**出场人物：** 陈九州、神秘男子
**出场道具：** 黑色请柬

△ 神秘男子递上黑色请柬，单膝点地。

**神秘男子**：少主，该回去了。

---

> [钩子] 本集钩子：黑色请柬上的家徽和旧疤吻合。
> [预告] 下集预告：陈九州赴宴，岳家全员震惊。

---

> **集末自查**
> [锚点] 节奏锚点：0-3s 冲突 [完成] | 30s 爆破 [完成] | 结尾钩子 [完成]
> [爽点] 爽点清单（≥3）：1.身份反差 2.直接打脸 3.危机钩
> [商业] 本集买单理由：想看陈九州身份揭晓那一刻。
> [商业] 付费/尾钩压力：请柬之约未兑现。
> [商业] 爽点兑现状态：蓄力
> [商业] 反派压力变化：王秀芳当众羞辱升级。

---
<!-- 剧本正文到此结束 -->
<!-- CONTINUITY
角色状态变化：陈九州隐忍值+1；身份线索首次出现。
伏笔与回收：黑色请柬（埋设 ep001，须 ep003 前兑现）。
尾钩义务：ep002 前 3 单元必须演请柬赴宴。
-->
"""

GOOD_COMIC = """# 第1集：白手套

> 本集关键词：溺亡、白手套、旧疤
> 本集爽点：悬疑钩、重生反差、操控反制
> 前情提要：无（本剧第一集）

---

## 1-1夜/内 公寓浴室

**出场人物：** 宋以安、凶手（仅见白手套）
**出场道具：** 白手套、浴缸

△ 水面静止。一只白手套缓缓收回。

**宋以安**（OS·冷静）：冷水。大概十五摄氏度。

---

## 1-2日/内 公司前台

**出场人物：** 宋以安、苏晴
**出场道具：** 工牌

**苏晴**（惊讶）：你昨天不是请假了？

**宋以安**（平静）：昨天。

（音效：电梯到站提示音）

---

> [钩子] 本集钩子：苏晴来电已接起。
> [预告] 下集预告：重生第一天上班，凶手就在身边。

---

> **集末自查**
> [锚点] 节奏锚点：0-3s 冲突 [完成] | 30s 爆破 [完成] | 结尾钩子 [完成]
> [爽点] 爽点清单（≥3）：1.悬疑钩 2.重生反差 3.操控反制
> [商业] 本集买单理由：想知道白手套是谁。
> [商业] 付费/尾钩压力：来电未接完。
> [商业] 爽点兑现状态：蓄力
> [商业] 反派压力变化：凶手身份压迫首次建立。

---
<!-- 剧本正文到此结束 -->
<!-- CONTINUITY
角色状态变化：宋以安重生，记忆完整。
伏笔与回收：白手套（埋设 ep001）。
尾钩义务：ep002 开场承接来电内容。
-->
"""


# --- E015 fixtures ---

# fixture A：模拟降级产出——裸对白 cue、多句连写、行间无空行
DEGRADED_BARE_CUE_A = """# 第3集：摊牌

> 本集关键词：摊牌、对峙、反转
> 本集爽点：当面对质、身份压制、危机钩
> 前情提要：陈九州收到黑色请柬。

---

## 3-1 · 内 · 苏家客厅 · 夜

**出场人物：** 陈九州、赵鹏程
**出场道具：** 黑色请柬

△ 赵鹏程把请柬拍在桌上。
赵鹏程：我来不是跟你作对的。你听我把话说完。
陈九州：说。
赵鹏程（冷笑）：你以为没人知道你是谁？请柬我也有一张。三天后的宴会，咱们都得去。
陈九州（OS）：他果然知道了。十年的局，今晚开始收网。

---

## 3-2 · 外 · 苏家门口 · 夜

**出场人物：** 陈九州、王秀芳
**出场道具：** 无

王秀芳：站住！你跟那个姓赵的说什么了？
陈九州：妈，没什么。

---

> [钩子] 本集钩子：赵鹏程也有请柬。
> [预告] 下集预告：宴会之夜，双请柬同场。

---

> **集末自查**
> [锚点] 节奏锚点：0-3s 冲突 [完成] | 30s 爆破 [完成] | 结尾钩子 [完成]
> [爽点] 爽点清单（≥3）：1.当面对质 2.身份压制 3.危机钩
> [商业] 本集买单理由：想看宴会摊牌。
> [商业] 付费/尾钩压力：双请柬之约未兑现。
> [商业] 爽点兑现状态：蓄力
> [商业] 反派压力变化：赵鹏程入局。

---
<!-- 剧本正文到此结束 -->
<!-- CONTINUITY
角色状态变化：赵鹏程身份线索公开。
伏笔与回收：双请柬（埋设 ep003）。
尾钩义务：ep004 开场必须进宴会场。
-->
"""

# fixture B：完全合规的现行模板剧本（在 GOOD_AI_LIVE 基础上补 OS cue + 表格行）
FULL_COMPLIANT_B = GOOD_AI_LIVE.replace(
    "**神秘男子**：少主，该回去了。",
    "**神秘男子**：少主，该回去了。\n\n"
    "**陈九州**（OS）：十年了，他们终于来了。\n\n"
    "| 镜头 | 时长 |\n| 特写请柬 | 2s |",
)

# fixture C：部分降级——场景头/元数据合规，仅一场对白是裸 cue
PARTIAL_DEGRADED_C = GOOD_AI_LIVE.replace(
    "**神秘男子**：少主，该回去了。",
    "神秘男子：少主，该回去了。我们等这一天等了十年。",
)

# fixture D（E016 命中）：复刻降级产出——同段逐行重复（2 处相邻对）+
# 跨段重复（1 处）= 预期 E016 共 3 处；△ 隔断处不命中。
# 这些行同时是裸 cue（半角冒号变体），E015 也应命中（5 处）。
ADJACENT_CUE_D = """# 第5集：劝降

> 本集关键词：劝降、合同、对峙
> 本集爽点：高价挖角、当面拒绝、危机钩
> 前情提要：赵鹏程登门挖角。

---

## 5-1 · 内 · 星脉会议室 · 夜

**出场人物：** 赵鹏程、林一
**出场道具：** 合同

△ 赵鹏程坐下，把公文包放在桌上。

赵鹏程: 我来不是跟你作对的。
赵鹏程: 我知道你的能力。
赵鹏程: A-0017，星脉最好的算法工程师。

△ 他把合同推过去

赵鹏程: 回来吧，我给你一个部门。
赵鹏程: 年薪200万，期权另算。

（BGM：低频压迫感，节奏渐紧）

---

> [钩子] 本集钩子：合同条款里藏着竞业陷阱。
> [预告] 下集预告：林一当面撕碎合同。

---

> **集末自查**
> [锚点] 节奏锚点：0-3s 冲突 [完成] | 30s 爆破 [完成] | 结尾钩子 [完成]
> [爽点] 爽点清单（≥3）：1.高价挖角 2.当面拒绝 3.危机钩
> [商业] 本集买单理由：想看林一怎么回应天价挖角。
> [商业] 付费/尾钩压力：合同未拆封。
> [商业] 爽点兑现状态：蓄力
> [商业] 反派压力变化：赵鹏程攻势升级。

---
<!-- 剧本正文到此结束 -->
<!-- CONTINUITY
角色状态变化：赵鹏程摊牌；林一守口。
伏笔与回收：竞业陷阱条款（埋设 ep005）。
尾钩义务：ep006 开场必须演撕合同。
-->
"""

# fixture E（E016 零命中）：合规剧本——同角色两条加粗 cue 被 △ 隔开 /
# 被其他角色台词隔开 / 被（音效：）隔开 / 加粗 cue 紧跟同名（OS）形态切换（必须不报）。
COMPLIANT_SPLIT_E = """# 第6集：账本

> 本集关键词：账本、试探、内心戏
> 本集爽点：细节反杀、口风对峙、危机钩
> 前情提要：林一拿到旧账本。

---

## 6-1 · 内 · 苏家书房 · 夜

**出场人物：** 陈九州、王秀芳
**出场道具：** 旧账本

△ 他翻开账本。

**陈九州**：我先看看。

△ 他停下手，指尖压住一行数字。

**陈九州**：这一页不对。

**王秀芳**：你懂什么？

**陈九州**：我懂的比你想的多。

（音效：门外脚步声由远及近）

**陈九州**：别说话。

---

## 6-2 · 内 · 书房门口 · 夜

**出场人物：** 陈九州
**出场道具：** 旧账本

**陈九州**：我没事。

**陈九州**（OS）：不能让她看出来。

---

> [钩子] 本集钩子：账本缺页编号和请柬家徽一致。
> [预告] 下集预告：缺页的下落浮出水面。

---

> **集末自查**
> [锚点] 节奏锚点：0-3s 冲突 [完成] | 30s 爆破 [完成] | 结尾钩子 [完成]
> [爽点] 爽点清单（≥3）：1.细节反杀 2.口风对峙 3.危机钩
> [商业] 本集买单理由：想知道缺页藏了什么。
> [商业] 付费/尾钩压力：脚步声主人未揭晓。
> [商业] 爽点兑现状态：蓄力
> [商业] 反派压力变化：王秀芳起疑。

---
<!-- 剧本正文到此结束 -->
<!-- CONTINUITY
角色状态变化：陈九州发现账本缺页。
伏笔与回收：缺页编号（埋设 ep006）。
尾钩义务：ep007 前 3 单元必须揭脚步声主人。
-->
"""

# fixture F（E015 边界）：半角冒号 cue、含空格角色名命中；
# 时刻（12:30）、URL（http://）、超 20 字符叙述句不误报。
HALFWIDTH_COLON_F = """# 第7集：交接

> 本集关键词：交接、列车、暗号
> 本集爽点：身份压制、暗号接头、危机钩
> 前情提要：神秘组织派人接头。

---

## 7-1 · 外 · 火车站站台 · 夜

**出场人物：** 赵鹏程、神秘男子 A
**出场道具：** 牛皮纸袋

赵鹏程: 这是你要的东西。

神秘男子 A：少主吩咐过，东西必须亲手交给你。

12:30 的列车进站。

他打开链接 http://example.com 看了一眼。

他在心里默默念着师父临走前留下的那句叮嘱的话：不要回头。

（BGM：列车进站轰鸣压过对话）

---

> [钩子] 本集钩子：纸袋里是半张照片。
> [预告] 下集预告：照片另一半在谁手里。

---

> **集末自查**
> [锚点] 节奏锚点：0-3s 冲突 [完成] | 30s 爆破 [完成] | 结尾钩子 [完成]
> [爽点] 爽点清单（≥3）：1.身份压制 2.暗号接头 3.危机钩
> [商业] 本集买单理由：想知道照片拼起来是谁。
> [商业] 付费/尾钩压力：照片只有一半。
> [商业] 爽点兑现状态：蓄力
> [商业] 反派压力变化：组织线收紧。

---
<!-- 剧本正文到此结束 -->
<!-- CONTINUITY
角色状态变化：赵鹏程交出纸袋。
伏笔与回收：半张照片（埋设 ep007）。
尾钩义务：ep008 开场必须接照片线。
-->
"""

# fixture G（E014 边界）：考据附录区带分隔行的 markdown 表格不报；
# 正文一处真实 `--` 报 1 处。
TABLE_SEP_G = GOOD_AI_LIVE.replace(
    "△ 神秘男子递上黑色请柬，单膝点地。",
    "△ 神秘男子递上黑色请柬，单膝点地。\n\n△ 他停顿了一下--然后转身。",
).replace(
    "<!-- 剧本正文到此结束 -->",
    """### 考据附录

| 条目 | 出处 |
| --- | --- |
| 请柬云纹 | 明代织物图谱 |

| 镜头 | 时值 |
|:---|---:|
| 特写请柬 | 2s |

---
<!-- 剧本正文到此结束 -->""",
)


def run_validator(tmp_path, content, *extra_args):
    ep = tmp_path / "ep001.md"
    ep.write_text(content, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(ep), "--json", *extra_args],
        capture_output=True, text=True, encoding="utf-8",
    )
    import json as _json
    report = _json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    return proc.returncode, report


class EpisodeValidateTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory(prefix="ep-validate-")
        self.tmp_path = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def codes(self, report, severity=None):
        return {
            f["code"] for f in report.get("findings", [])
            if severity is None or f["severity"] == severity
        }

    def test_good_ai_live_passes(self):
        rc, report = run_validator(self.tmp_path, GOOD_AI_LIVE, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 0, report)
        self.assertEqual(self.codes(report, "HARD"), set())

    def test_good_comic_passes(self):
        rc, report = run_validator(self.tmp_path, GOOD_COMIC, "--medium", "comic", "--mode", "domestic")
        self.assertEqual(rc, 0, report)
        self.assertEqual(self.codes(report, "HARD"), set())

    def test_medium_auto_detects_comic(self):
        rc, report = run_validator(self.tmp_path, GOOD_COMIC)
        self.assertEqual(report.get("medium"), "comic")
        self.assertEqual(rc, 0, report)

    def test_backtick_scene_header_fails(self):
        # 故障案例缺陷 #3：场景头带 backtick / 错分隔
        broken = GOOD_COMIC.replace("## 1-1夜/内 公寓浴室", "## `1-1 夜/内 公寓浴室`")
        rc, report = run_validator(self.tmp_path, broken, "--medium", "comic", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertIn("E005", self.codes(report, "HARD"))

    def test_missing_boundary_marker_fails(self):
        # 故障案例缺陷 #4
        broken = GOOD_AI_LIVE.replace("<!-- 剧本正文到此结束 -->\n", "")
        rc, report = run_validator(self.tmp_path, broken, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertIn("E008", self.codes(report, "HARD"))

    def test_missing_continuity_block_fails(self):
        # 故障案例缺陷 #5
        broken = GOOD_AI_LIVE[: GOOD_AI_LIVE.index("<!-- CONTINUITY")]
        rc, report = run_validator(self.tmp_path, broken, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertIn("E009", self.codes(report, "HARD"))

    def test_missing_metadata_fails(self):
        # 故障案例缺陷 #7/#8
        broken = GOOD_AI_LIVE.replace("> 本集关键词：入赘受辱、隐藏战神、旧疤疑云\n", "")
        broken = broken.replace("> 本集爽点：身份反差、直接打脸、危机钩\n", "")
        rc, report = run_validator(self.tmp_path, broken, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertTrue({"E002", "E003"} <= self.codes(report, "HARD"))

    def test_missing_cast_props_lines_fail(self):
        # 故障案例缺陷 #9/#10
        broken = GOOD_AI_LIVE.replace("**出场人物：** 陈九州、王秀芳\n", "").replace(
            "**出场道具：** 缺口瓷碗\n", "")
        rc, report = run_validator(self.tmp_path, broken, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertTrue({"E006", "E007"} <= self.codes(report, "HARD"))

    def test_missing_hook_preview_tags_fail(self):
        # 故障案例缺陷 #12/#13
        broken = GOOD_AI_LIVE.replace("> [钩子] 本集钩子：黑色请柬上的家徽和旧疤吻合。\n", "")
        broken = broken.replace("> [预告] 下集预告：陈九州赴宴，岳家全员震惊。\n", "")
        rc, report = run_validator(self.tmp_path, broken, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertTrue({"E010", "E011"} <= self.codes(report, "HARD"))

    def test_missing_self_check_tags_fail(self):
        # 故障案例缺陷 #14：自查用表格而非标签
        broken = GOOD_AI_LIVE
        for tag in ("[锚点]", "[爽点]", "[商业]"):
            broken = "\n".join(l for l in broken.splitlines() if tag not in l)
        rc, report = run_validator(self.tmp_path, broken + "\n", "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertIn("E012", self.codes(report, "HARD"))

    def test_comic_four_scenes_fails_h1(self):
        extra_scene = """
## 1-3日/内 茶水间

**出场人物：** 宋以安
**出场道具：** 纸杯

△ 纸杯落地。

## 1-4夜/外 天台

**出场人物：** 宋以安
**出场道具：** 手机

△ 手机亮起。
"""
        broken = GOOD_COMIC.replace("---\n\n> [钩子]", extra_scene + "\n---\n\n> [钩子]")
        rc, report = run_validator(self.tmp_path, broken, "--medium", "comic", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertIn("E013", self.codes(report, "HARD"))

    def test_dash_in_dialogue_fails(self):
        broken = GOOD_AI_LIVE.replace("妈，我来收拾。", "妈——我来收拾。")
        rc, report = run_validator(self.tmp_path, broken, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertIn("E014", self.codes(report, "HARD"))

    def test_hr_lines_do_not_trigger_dash_ban(self):
        rc, report = run_validator(self.tmp_path, GOOD_AI_LIVE, "--medium", "ai_live", "--mode", "domestic")
        self.assertNotIn("E014", self.codes(report))

    def test_empty_tail_hook_obligation_warns(self):
        broken = GOOD_AI_LIVE.replace("尾钩义务：ep002 前 3 单元必须演请柬赴宴。", "尾钩义务：")
        rc, report = run_validator(self.tmp_path, broken, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 0)  # WARN 不阻断
        self.assertIn("W005", self.codes(report, "WARN"))

    def test_two_cues_in_one_paragraph_warns(self):
        broken = GOOD_AI_LIVE.replace(
            "**王秀芳**（冷笑）：吃白饭的也配上桌？\n\n**陈九州**：妈，我来收拾。",
            "**王秀芳**（冷笑）：吃白饭的也配上桌？\n**陈九州**：妈，我来收拾。",
        )
        rc, report = run_validator(self.tmp_path, broken, "--medium", "ai_live", "--mode", "domestic")
        self.assertIn("W004", self.codes(report, "WARN"))

    # --- E015 裸对白 cue ---

    def test_bare_cue_degraded_episode_fails_e015(self):
        # fixture A：降级产出，6 行裸 cue 全部命中
        rc, report = run_validator(self.tmp_path, DEGRADED_BARE_CUE_A, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        self.assertIn("E015", self.codes(report, "HARD"))
        e015 = [f for f in report["findings"] if f["code"] == "E015"]
        self.assertEqual(len(e015), 6, e015)

    def test_compliant_template_no_e015_false_positive(self):
        # fixture B：合规模板（含 **名**：/**名**（冷笑）：/**名**（OS）：/△/出场人物/BGM/>元数据/表格行）零误报
        rc, report = run_validator(self.tmp_path, FULL_COMPLIANT_B, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 0, report)
        self.assertNotIn("E015", self.codes(report))
        self.assertEqual(self.codes(report, "HARD"), set())

    def test_partial_degraded_single_bare_cue_fails_e015(self):
        # fixture C：仅一场对白降级为裸 cue，恰好命中 1 处
        rc, report = run_validator(self.tmp_path, PARTIAL_DEGRADED_C, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        e015 = [f for f in report["findings"] if f["code"] == "E015"]
        self.assertEqual(len(e015), 1, e015)
        self.assertIn("神秘男子", e015[0]["message"])

    # --- E016 相邻同名同形态 cue ---

    def test_adjacent_same_speaker_cue_fails_e016(self):
        # fixture D：同段逐行重复 2 处 + 跨段重复 1 处 = 3 处；△ 隔断处不命中
        rc, report = run_validator(self.tmp_path, ADJACENT_CUE_D, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        e016 = [f for f in report["findings"] if f["code"] == "E016"]
        self.assertEqual(len(e016), 3, e016)
        self.assertTrue(all("赵鹏程" in f["message"] for f in e016))
        self.assertTrue(all(f["severity"] == "HARD" for f in e016))
        # 同批裸 cue（半角冒号变体）E015 同步命中 5 处
        e015 = [f for f in report["findings"] if f["code"] == "E015"]
        self.assertEqual(len(e015), 5, e015)

    def test_compliant_split_cues_no_e016_false_positive(self):
        # fixture E：△ 隔开 / 他人台词隔开 / （音效：）隔开 / 同名 form 切换（normal→OS）零命中
        rc, report = run_validator(self.tmp_path, COMPLIANT_SPLIT_E, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 0, report)
        self.assertNotIn("E016", self.codes(report))
        self.assertEqual(self.codes(report, "HARD"), set())

    # --- E015 半角冒号 / 含空格角色名 ---

    def test_halfwidth_colon_and_spaced_name_e015(self):
        # fixture F：`赵鹏程: ` 半角冒号 + `神秘男子 A：` 含空格名命中（2 处）；
        # 12:30 / http:// / 超 20 字符叙述句不误报
        rc, report = run_validator(self.tmp_path, HALFWIDTH_COLON_F, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        e015 = [f for f in report["findings"] if f["code"] == "E015"]
        self.assertEqual(len(e015), 2, e015)
        messages = "".join(f["message"] for f in e015)
        self.assertIn("赵鹏程", messages)
        self.assertIn("神秘男子 A", messages)
        self.assertNotIn("E016", self.codes(report))

    # --- E014 表格分隔行豁免 ---

    def test_table_separator_rows_exempt_from_e014(self):
        # fixture G：`| --- | --- |` / `|:---|---:|` 不报；正文真实 `--` 报 1 处
        rc, report = run_validator(self.tmp_path, TABLE_SEP_G, "--medium", "ai_live", "--mode", "domestic")
        self.assertEqual(rc, 2)
        e014 = [f for f in report["findings"] if f["code"] == "E014"]
        self.assertEqual(len(e014), 1, e014)
        self.assertIn("然后转身", e014[0]["message"])

    def test_project_state_resolves_medium_mode(self):
        state = self.tmp_path / ".drama-state.json"
        state.write_text('{"medium": "ai_live", "mode": "domestic"}', encoding="utf-8")
        (self.tmp_path / "episodes").mkdir()
        ep = self.tmp_path / "episodes" / "ep001.md"
        ep.write_text(GOOD_AI_LIVE, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(ep), "--json", "--project", str(self.tmp_path)],
            capture_output=True, text=True, encoding="utf-8",
        )
        import json as _json
        report = _json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(report["medium"], "ai_live")
        self.assertEqual(report["mode"], "domestic")


if __name__ == "__main__":
    unittest.main()
